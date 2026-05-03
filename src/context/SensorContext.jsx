import { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'
import SensorAggregator from '../utils/sensorAggregator'
import { initKeyboardTracker } from '../utils/keyboardTracker'
import { startPeriodicRefresh } from '../services/newsEngine'

const SensorContext = createContext(null)

// Worker file URLs
const FACE_WORKER_URL = new URL('../workers/faceWorker.js', import.meta.url)
const VOICE_WORKER_URL = new URL('../workers/voiceWorker.js', import.meta.url)
const FUSION_WORKER_URL = new URL('../workers/fusionWorker.js', import.meta.url)

export function SensorProvider({ children }) {
  // State
  const [sensorActive, setSensorActive] = useState(false)
  const [sensorError, setSensorError] = useState(null)
  const [faceData, setFaceData] = useState(null)
  const [voiceData, setVoiceData] = useState(null)
  const [keyboardData, setKeyboardData] = useState(null)
  const [bufferFill, setBufferFill] = useState(0)

  // Fusion state
  const [fusionActive, setFusionActive] = useState(false)
  const [fusionResult, setFusionResult] = useState(null)
  const [fusionError, setFusionError] = useState(null)

  // Refs to hold persistent objects
  const aggregatorRef = useRef(new SensorAggregator(50))
  const faceWorkerRef = useRef(null)
  const voiceWorkerRef = useRef(null)
  const fusionWorkerRef = useRef(null)
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const audioContextRef = useRef(null)
  const processorRef = useRef(null)
  const cleanupKeyboardRef = useRef(null)
  const fusionLoopId = useRef(null)

  /**
   * Initialize and start all sensors.
   */
  const startSensors = async () => {
    setSensorError(null)

    try {
      // 1. Initialize camera
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: { sampleRate: 16000, channelCount: 1 }
      })
      streamRef.current = stream

      // Create hidden video element
      const video = document.createElement('video')
      video.srcObject = stream
      video.playsInline = true
      await video.play()
      videoRef.current = video

      // 2. Create Face Worker
      const faceWorker = new Worker(FACE_WORKER_URL, { type: 'module' })
      faceWorkerRef.current = faceWorker

      faceWorker.onmessage = (e) => {
        const { type, gaze_x, gaze_y, au, timestamp } = e.data
        if (type === 'result') {
          setFaceData({ gaze_x, gaze_y, au })
          aggregatorRef.current.push({
            timestamp,
            face: { gaze_x, gaze_y, au }
          })
          setBufferFill(aggregatorRef.current.getFillLevel())
        } else if (type === 'error') {
          console.error('[FaceWorker]', e.data.message)
        }
        // 'no-face' is ignored
      }

      faceWorker.postMessage({ type: 'init' })

      // 3. Create Voice Worker
      const voiceWorker = new Worker(VOICE_WORKER_URL, { type: 'module' })
      voiceWorkerRef.current = voiceWorker

      voiceWorker.onmessage = (e) => {
        const { type, mfcc, pitch, loudness, jitter, shimmer, timestamp } = e.data
        if (type === 'result') {
          setVoiceData({ mfcc, pitch, loudness, jitter, shimmer })
          // Merge with any existing face data from same timestamp
          const current = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
          if (current && !current.voice) {
            current.voice = { mfcc, pitch, loudness, jitter, shimmer }
          } else {
            aggregatorRef.current.push({
              timestamp,
              voice: { mfcc, pitch, loudness, jitter, shimmer }
            })
          }
          setBufferFill(aggregatorRef.current.getFillLevel())
        } else if (type === 'error') {
          console.error('[VoiceWorker]', e.data.message)
        }
      }

      // 4. Connect audio stream to voice worker via AudioWorklet or ScriptProcessor
      const audioCtx = new AudioContext({ sampleRate: 16000 })
      audioContextRef.current = audioCtx
      const source = audioCtx.createMediaStreamSource(stream)
      const processor = audioCtx.createScriptProcessor(4096, 1, 1)

      processor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer.getChannelData(0)
        // Copy buffer and send to worker
        const bufferCopy = new Float32Array(inputBuffer)
        voiceWorker.postMessage(
          { type: 'audio', buffer: bufferCopy, sampleRate: 16000, timestamp: performance.now() },
          [bufferCopy.buffer]  // transfer
        )
      }

      source.connect(processor)
      processor.connect(audioCtx.destination)
      processorRef.current = processor

      // 5. Initialize Keyboard Tracker
      const cleanupKeyboard = initKeyboardTracker((kbData) => {
        setKeyboardData(kbData)
        const current = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
        if (current && !current.keyboard) {
          current.keyboard = kbData
        } else {
          aggregatorRef.current.push({
            timestamp: performance.now(),
            keyboard: kbData
          })
        }
        setBufferFill(aggregatorRef.current.getFillLevel())
      })
       cleanupKeyboardRef.current = cleanupKeyboard

      // 7. Initialize Fusion Worker
      const fusionWorker = new Worker(FUSION_WORKER_URL, { type: 'module' })
      fusionWorkerRef.current = fusionWorker

      fusionWorker.onmessage = (e) => {
        const { type, intentProbabilities, embedding, confidence, deceptionProbability, timestamp } = e.data
        if (type === 'result') {
          setFusionResult({ intentProbabilities, embedding, confidence, deceptionProbability, timestamp })
          setFusionActive(true)
        } else if (type === 'error') {
          console.error('[FusionWorker]', e.data.message)
          setFusionError(e.data.message)
        } else if (type === 'ready') {
          console.log('[FusionWorker] Model ready – inference enabled')
          setFusionActive(true)
        }
      }

      fusionWorker.postMessage({ type: 'init' })

      // 8. Start fusion inference loop at 20Hz (50ms interval)
      const FUSION_INTERVAL_MS = 50
      const runFusion = () => {
        if (aggregatorRef.current.getFillLevel() >= 50) {
          const tensor = aggregatorRef.current.getTensorInput()
          fusionWorker.postMessage({ type: 'tensor', data: tensor })
        }
        fusionLoopId.current = requestAnimationFrame(runFusion)
      }
      // Use setTimeout to start after a small delay, then use RAF for timing
      setTimeout(() => {
        runFusion()
      }, 500)

      // 6. Subscribe aggregator to updates (kept for logging)
      aggregatorRef.current.subscribe((buffer, vector) => {
        if (buffer.length % 10 === 0) {
          console.log('[Aggregator] Buffer:', buffer.length, '/50')
        }
      })

      setSensorActive(true)
      console.log('[SensorContext] All sensors started')

    } catch (err) {
      console.error('[SensorContext] startup error:', err)
      setSensorError(`Could not start sensors: ${err.message}`)
    }
  }

  /**
   * Stop all sensors and cleanup.
   */
  const stopSensors = useCallback(() => {
    // Stop camera
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }

    // Stop audio processing
    if (processorRef.current) {
      processorRef.current.disconnect()
      processorRef.current = null
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

     // Terminate workers
     if (faceWorkerRef.current) {
       faceWorkerRef.current.postMessage({ type: 'close' })
       faceWorkerRef.current.terminate()
       faceWorkerRef.current = null
     }
     if (voiceWorkerRef.current) {
       voiceWorkerRef.current.postMessage({ type: 'close' })
       voiceWorkerRef.current.terminate()
       voiceWorkerRef.current = null
     }
     if (fusionWorkerRef.current) {
       fusionWorkerRef.current.postMessage({ type: 'close' })
       fusionWorkerRef.current.terminate()
       fusionWorkerRef.current = null
     }
     if (fusionLoopId.current) {
       cancelAnimationFrame(fusionLoopId.current)
       fusionLoopId.current = null
     }

    // Stop keyboard tracker
    if (cleanupKeyboardRef.current) {
      cleanupKeyboardRef.current()
      cleanupKeyboardRef.current = null
    }

    // Reset state
    setSensorActive(false)
    setFaceData(null)
    setVoiceData(null)
    setKeyboardData(null)
    aggregatorRef.current.reset()
    setBufferFill(0)

    console.log('[SensorContext] Sensors stopped')
  }, [])

  // Start periodic news refresh on mount
  useEffect(() => {
    startPeriodicRefresh(5 * 60 * 1000) // every 5 minutes
    return () => {}
  }, [])

  const value = {
    sensorActive,
    sensorError,
    faceData,
    voiceData,
    keyboardData,
    bufferFill,
    startSensors,
    stopSensors,
    aggregator: aggregatorRef.current,
    // Expose latest vector for model inference
    getLatestVector: () => aggregatorRef.current.getLatestVector(),
    getTensorInput: () => aggregatorRef.current.getTensorInput(),
    // Fusion state
    fusionActive,
    fusionResult,
    fusionError
  }

  return (
    <SensorContext.Provider value={value}>
      {children}
    </SensorContext.Provider>
  )
}

export function useSensor() {
  const context = useContext(SensorContext)
  if (!context) {
    throw new Error('useSensor must be used within a SensorProvider')
  }
  return context
}
