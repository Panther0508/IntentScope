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
 *
 * FALLBACK: If ONNX model fails to load, operates in simulation mode
 * using a weighted heuristic based on recent sensor statistics.
 */

import { InferenceSession, Tensor } from 'onnxruntime-web'

let session = null
let isReady = false
let useSimulation = false  // Flag for fallback mode
let inputName = 'input'
let outputNames = ['intent_logits', 'embedding']

// Intent labels matching the training pipeline
const INTENT_LABELS = [
  'Exploring', 'BuyIntent', 'Hesitation', 'Deception',
  'ActionConfirm', 'RobotPick', 'RobotPlace', 'RobotIdle'
]

// Simulation mode: TODO: add temporal history for smoothing

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
 * Generate a deterministic embedding from current stats (simulation fallback)
 */
function generateEmbedding(stats) {
  // Pseudo-random but deterministic based on stats
  const seed = stats.reduce((a, b) => a + Math.abs(b), 0) * 1000
  const embedding = new Float32Array(32)
  for (let i = 0; i < 32; i++) {
    embedding[i] = Math.sin(seed + i) * 0.5 + 0.5
  }
  return embedding
}

/**
 * Heuristic intent prediction based on sensor feature statistics
 * Used when ONNX model is unavailable.
 */
function simulateIntent(tensorData) {
  // Extract key features (approximate indices based on sensorAggregator)
  // Indices: 0-12 MFCC mean, 13 pitch mean, 14 loudness mean, 15-18 AU mean, 19-20 gaze mean, 21-27 keyboard stats
  const mfccMean = tensorData.slice(0, 13).reduce((a, b) => a + b, 0) / 13
  const pitchMean = tensorData[13]
  const loudnessMean = tensorData[14]
  const browRaise = tensorData[16]  // AU: brow raise
  const eyeGazeX = tensorData[19]
  const eyeGazeY = tensorData[20]
  const typingSpeed = tensorData[24]  // typing_speed norm
  const hesitation = tensorData[27]   // hesitation_score

  // Normalize approximate ranges
  // Features roughly in [-1,1] or [0,1] from aggregator

  // Initialize logits with base
  const logits = new Array(8).fill(0)

  // Heuristics:
  // - High brow raise + steady gaze → Exploring/interest
  if (browRaise > 0.3 && Math.abs(eyeGazeX) < 0.3) {
    logits[0] += 2.0  // Exploring
  }
  // - High pitch + loudness variability → Hesitation/BuyIntent
  if (pitchMean > 0.6 && loudnessMean > 0.5) {
    logits[2] += 1.5  // Hesitation
    logits[1] += 1.0  // BuyIntent
  }
  // - Low pitch + steady typing → ActionConfirm/RobotPick
  if (pitchMean < 0.4 && typingSpeed > 0.6) {
    logits[4] += 1.5  // ActionConfirm
    logits[5] += 1.0  // RobotPick
  }
  // - High hesitation score → Deception
  if (hesitation > 0.6) {
    logits[3] += 2.5  // Deception
  }
  // - Gaze looking down/away + high AU → RobotPlace
  if (eyeGazeY > 0.4 && browRaise < 0) {
    logits[6] += 1.0  // RobotPlace
  }
  // Default to RobotIdle if nothing strong
  if (logits.every(v => v === 0)) {
    logits[7] = 1.0  // RobotIdle
  }

  const probs = softmax(logits)
  const intentProbabilities = {}
  INTENT_LABELS.forEach((label, i) => {
    intentProbabilities[label] = probs[i]
  })

  const confidence = Math.max(...probs)
  const deceptionProbability = intentProbabilities['Deception']

  // Stats for embedding generation
  const stats = [mfccMean, pitchMean, loudnessMean, browRaise, eyeGazeX, eyeGazeY, typingSpeed, hesitation]
  const embedding = generateEmbedding(stats)

  return {
    intentProbabilities,
    embedding,
    confidence,
    deceptionProbability
  }
}

/**
 * Initialise the ONNX model.
 * Loads from public/fusion_model.onnx (served as static asset).
 * Falls back to simulation mode if model fails to load.
 */
async function initModel() {
  try {
    console.log('[FusionWorker] Loading ONNX model...')

    // URL to the model – works both in dev and prod
    const modelUrl = '/fusion_model.onnx'

    session = await InferenceSession.create(modelUrl, {
      executionProviders: ['wasm', 'webgl', 'cpu'],  // prefer WASM for determinism
      graphOptimizationLevel: 'all'
    })

    inputName = session.inputNames[0]
    outputNames = session.outputNames

    console.log(`[FusionWorker] Model loaded. Input: ${inputName}, Outputs: ${outputNames.join(', ')}`)
    isReady = true
    useSimulation = false
    self.postMessage({ type: 'ready', mode: 'onnx' })

  } catch (err) {
    console.warn('[FusionWorker] ONNX load failed, entering simulation mode:', err.message)
    useSimulation = true
    isReady = true  // Still ready, just using heuristics
    self.postMessage({
      type: 'ready',
      mode: 'simulation',
      warning: 'Using heuristic fallback – real model not found. Train it: python training/train_fusion_model.py'
    })
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
 * Uses ONNX if loaded, otherwise simulation heuristic.
 */
async function infer(tensor) {
  if (!isReady) {
    throw new Error('Model not ready')
  }

  // Simulation mode: use heuristic
  if (useSimulation) {
    const flatData = Array.from(tensor.data)
    const result = simulateIntent(flatData)
    return {
      ...result,
      timestamp: performance.now()
    }
  }

  // ONNX mode
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
