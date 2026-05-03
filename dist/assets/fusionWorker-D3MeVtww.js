/**
 * Fusion Worker – Real-time Intent Prediction via ONNX Runtime Web
 * ================================================================
 * Loads the fused LSTM model (intent + embedding) and runs inference
 * on 50-timestep, 28-feature sliding windows at up to 20 Hz.
 *
 * Messages from main thread:
 *   { type: 'tensor', data: Float32Array, shape: [1,50,28] }
 *
 * Messages to main thread:
 *   { type: 'result',
 *     intentProbabilities: {Exploring, BuyIntent, ..., RobotIdle},
 *     embedding: Float32Array(32),
 *     confidence: number,
 *     deceptionProbability: number,
 *     timestamp: number }
 *
 *   { type: 'error', message: string }
 *   { type: 'ready' } when model loaded
 */

import { InferenceSession, Tensor } from 'onnxruntime-web'

let session = null
let isReady = false
let inputName = 'input'
let outputNames = ['intent_logits', 'embedding']

// Intent labels matching the training pipeline
const INTENT_LABELS = [
  'Exploring', 'BuyIntent', 'Hesitation', 'Deception',
  'ActionConfirm', 'RobotPick', 'RobotPlace', 'RobotIdle'
]

/**
 * Softmax helper (in case ONNX doesn't include it)
 */
function softmax(arr) {
  const max = Math.max(...arr)
  const exps = arr.map(x => Math.exp(x - max))
  const sum = exps.reduce((a, b) => a + b, 0)
  return exps.map(x => x / sum)
}

/**
 * Initialise the ONNX model.
 * Loads from public/fusion_model.onnx (served as static asset).
 */
async function initModel() {
  try {
    console.log('[FusionWorker] Loading ONNX model...')

    // URL to the model – works both in dev and prod
    const modelUrl = '/fusion_model.onnx'

    session = await InferenceSession.create(modelUrl, {
      executionProviders: ['wasm', 'webgl', 'cpu'],  // prefer WASM for确定性
      graphOptimizationLevel: 'all'
    })

    inputName = session.inputNames[0]
    outputNames = session.outputNames

    console.log(`[FusionWorker] Model loaded. Input: ${inputName}, Outputs: ${outputNames.join(', ')}`)
    isReady = true
    self.postMessage({ type: 'ready' })

  } catch (err) {
    console.error('[FusionWorker] Model load error:', err)
    self.postMessage({ type: 'error', message: `ONNX model failed to load: ${err.message}` })
  }
}

/**
 * Preprocess tensor: ensure shape (1, 50, 28) Float32.
 * Main thread should send exactly that, but we guard anyway.
 */
function prepareTensor(data) {
  if (data instanceof Float32Array && data.length === 50 * 28) {
    return new Tensor('float32', data, [1, 50, 28])
  } else if (Array.isArray(data)) {
    // Flatten and wrap
    const flat = new Float32Array(data.flat())
    return new Tensor('float32', flat, [1, 50, 28])
  } else {
    throw new Error(`Invalid tensor shape: expected 1400 elements, got ${data?.length}`)
  }
}

/**
 * Run a single inference pass.
 */
async function infer(tensor) {
  if (!session || !isReady) {
    throw new Error('Model not ready')
  }

  const feeds = { [inputName]: tensor }
  const results = await session.run(feeds)

  // Extract outputs
  const logitsTensor = results[outputNames[0]]  // shape (1, 8)
  const embedTensor = results[outputNames[1]]  // shape (1, 32)

  const logits = Array.from(logitsTensor.data)
  const probs = softmax(logits)
  const embedding = new Float32Array(embedTensor.data)

  // Build probability map
  const intentProbabilities = {}
  INTENT_LABELS.forEach((label, i) => {
    intentProbabilities[label] = probs[i]
  })

  // Confidence is max probability
  const confidence = Math.max(...probs)
  const deceptionProbability = intentProbabilities['Deception']

  return {
    intentProbabilities,
    embedding,
    confidence,
    deceptionProbability,
    timestamp: performance.now()
  }
}

// ── Message handling ────────────────────────────────────────────────────────
self.onmessage = async (event) => {
  const { type, data } = event.data

  if (type === 'init') {
    await initModel()
    return
  }

  if (type === 'tensor') {
    if (!isReady) {
      self.postMessage({ type: 'error', message: 'Model not ready – initializing...' })
      return
    }

    try {
      const tensor = prepareTensor(data)
      const result = await infer(tensor)
      self.postMessage({ type: 'result', ...result })
    } catch (err) {
      console.error('[FusionWorker] Inference error:', err)
      self.postMessage({ type: 'error', message: err.message })
    }
    return
  }

  if (type === 'close') {
    self.close()
    return
  }
}

// Auto-initialize
initModel().catch(err => {
  console.error('[FusionWorker] Init failed:', err)
  self.postMessage({ type: 'error', message: err.message })
})
