/**
 * Face & Gaze Worker
 * Uses MediaPipe FaceLandmarker to extract facial action units and gaze direction.
 *
 * Messages from main thread:
 *   { type: 'frame', imageBitmap: ImageBitmap, timestamp: number }
 *
 * Messages to main thread:
 *   { type: 'result', gaze_x: 0–1, gaze_y: 0–1, au: { AU1, AU2, AU12, AU15, AU20, AU26 }, timestamp: number }
 *   or { type: 'no-face' }
 */

import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision'

let faceLandmarker = null
let isReady = false

// AU landmark indices (approximations based on MediaPipe face mesh)
// These are simplified geometric proxies – actual AUs require complex deformation modeling
const LANDMARKS = {
  // Brow raisers (AU1, AU2)
  left_brow_inner: 107,
  left_brow_outer: 70,
  right_brow_inner: 336,
  right_brow_outer: 300,
  // Lip corner puller (AU12)
  mouth_left: 61,
  mouth_right: 291,
  mouth_top: 13,
  mouth_bottom: 14,
  // Lip tightener / depressor (AU15)
  mouth_corner_left: 61,
  mouth_corner_right: 291,
  // Chin raiser (AU17)
  chin: 152,
  // Jaw drop (AU26)
  jaw: 152,  // same point, measured via mouth opening
  // Iris for gaze (MediaPipe provides iris centers: 468 left, 473 right)
  left_iris: 468,
  right_iris: 473,
  // Eye corners for gaze direction
  left_eye_left: 33,
  left_eye_right: 133,
  right_eye_left: 362,
  right_eye_right: 263
}

function euclidean(p1, p2) {
  return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
}

function verticalDelta(p1, p2) {
  return Math.abs(p1.y - p2.y)
}

// AU computation helpers

function computeAU1(landmarks) {  // inner brow raiser
  const left = euclidean(landmarks[LANDMARKS.left_brow_inner], landmarks[LANDMARKS.left_eye_left])
  const right = euclidean(landmarks[LANDMARKS.right_brow_inner], landmarks[LANDMARKS.right_eye_right])
  return ((left + right) / 2 - 0.08) * 10  // calibrated roughly
}

function computeAU2(landmarks) {  // outer brow raiser
  const left = euclidean(landmarks[LANDMARKS.left_brow_outer], landmarks[LANDMARKS.left_eye_left])
  const right = euclidean(landmarks[LANDMARKS.right_brow_outer], landmarks[LANDMARKS.right_eye_right])
  return ((left + right) / 2 - 0.12) * 10
}

function computeAU12(landmarks) {  // lip corner puller (smile)
  const mouth_width = euclidean(landmarks[LANDMARKS.mouth_left], landmarks[LANDMARKS.mouth_right])
  const baseline = 0.25  // approximate neutral width
  return Math.max(0, (mouth_width - baseline) / baseline)
}

function computeAU15(landmarks) {  // lip corner depressor
  const left = verticalDelta(landmarks[LANDMARKS.mouth_corner_left], landmarks[LANDMARKS.mouth_top])
  const right = verticalDelta(landmarks[LANDMARKS.mouth_corner_right], landmarks[LANDMARKS.mouth_top])
  return ((left + right) / 2 - 0.02) * 20
}

function computeAU20(landmarks) {  // lip stretcher
  const mouth_width = euclidean(landmarks[LANDMARKS.mouth_left], landmarks[LANDMARKS.mouth_right])
  return Math.max(0, mouth_width - 0.3) * 5
}

function computeAU26(landmarks) {  // jaw drop
  const mouthOpen = Math.abs(landmarks[LANDMARKS.mouth_top].y - landmarks[LANDMARKS.mouth_bottom].y)
  return Math.min(1, mouthOpen * 5)
}

// Simple gaze from iris position relative to eye bounding box
function computeGaze(landmarks) {
  const leftIris = landmarks[LANDMARKS.left_iris]
  const rightIris = landmarks[LANDMARKS.right_iris]
  const leftOuter = landmarks[LANDMARKS.left_eye_left]
  const leftInner = landmarks[LANDMARKS.left_eye_right]
  const rightOuter = landmarks[LANDMARKS.right_eye_left]
  const rightInner = landmarks[LANDMARKS.right_eye_right]

  // Normalize x position within each eye from 0 (inner) to 1 (outer)
  const leftGazeX = (leftIris.x - leftInner.x) / (leftOuter.x - leftInner.x + 1e-6)
  const rightGazeX = (rightIris.x - rightInner.x) / (rightOuter.x - rightInner.x + 1e-6)

  // Average across eyes, flip so center = 0.5
  const gazeX = 1 - ((leftGazeX + rightGazeX) / 2)

  // Y gaze from vertical position relative to eye center
  const leftEyeCenterY = (leftOuter.y + leftInner.y) / 2
  const rightEyeCenterY = (rightOuter.y + rightInner.y) / 2
  const leftGazeY = (leftIris.y - leftEyeCenterY) * 3  // amplification
  const rightGazeY = (rightIris.y - rightEyeCenterY) * 3
  const gazeY = 0.5 + ((leftGazeY + rightGazeY) / 2)

  return {
    x: Math.max(0, Math.min(1, gazeX)),
    y: Math.max(0, Math.min(1, gazeY))
  }
}

// Initialize MediaPipe
async function init() {
  if (faceLandmarker) return

  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'
  )

  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
      delegate: 'GPU'  // fallback to CPU if unavailable
    },
    outputFaceBlendshapes: false,
    outputFacialTransformationMatrixes: false,
    runningMode: 'VIDEO',
    numFaces: 1
  })

  isReady = true
  self.postMessage({ type: 'ready' })
  console.log('[FaceWorker] MediaPipe FaceLandmarker initialized')
}

// Process single frame
function detect(imageBitmap, timestamp) {
  if (!isReady || !faceLandmarker) return

  const result = faceLandmarker.detectForVideo(imageBitmap, timestamp)

  if (result.faceLandmarks && result.faceLandmarks.length > 0) {
    const landmarks = result.faceLandmarks[0]

    // Compute AUs
    const au = {
      AU1: Math.min(1, Math.max(0, computeAU1(landmarks))),
      AU2: Math.min(1, Math.max(0, computeAU2(landmarks))),
      AU12: Math.min(1, Math.max(0, computeAU12(landmarks))),
      AU15: Math.min(1, Math.max(0, computeAU15(landmarks))),
      AU20: Math.min(1, Math.max(0, computeAU20(landmarks))),
      AU26: Math.min(1, Math.max(0, computeAU26(landmarks)))
    }

    // Compute gaze
    const gaze = computeGaze(landmarks)

    self.postMessage({
      type: 'result',
      gaze_x: gaze.x,
      gaze_y: gaze.y,
      au,
      timestamp
    })
  } else {
    self.postMessage({ type: 'no-face', timestamp })
  }
}

// ── Message handling ────────────────────────────────────────────────────────
self.onmessage = async (event) => {
  const { type, imageBitmap, timestamp } = event.data

  if (type === 'init') {
    await init()
  } else if (type === 'frame') {
    detect(imageBitmap, timestamp)
  } else if (type === 'close') {
    self.close()
  }
}

// Auto-initialize on startup
init().catch(err => {
  console.error('[FaceWorker] Init failed:', err)
  self.postMessage({ type: 'error', message: err.message })
})
