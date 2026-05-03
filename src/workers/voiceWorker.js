/**
 * Voice Stress Worker
 * Uses Meyda to extract audio features from raw Float32Array buffers.
 *
 * Input: Raw PCM audio (mono, 16kHz, float32)
 * Output: { mfcc: [...13...], pitch, loudness, jitter, shimmer, timestamp }
 */

import { extract } from 'meyda'

const PITCH_HISTORY = []
const AMPLITUDE_HISTORY = []
const HISTORY_SIZE = 20

// Helper NumPy-like functions
const np = {
  mean: arr => arr.reduce((a, b) => a + b, 0) / arr.length,
  std: arr => {
    if (arr.length < 2) return 0
    const m = np.mean(arr)
    const variance = arr.reduce((s, v) => s + (v - m) ** 2, 0) / (arr.length - 1)
    return Math.sqrt(variance)
  },
  median: arr => {
    const sorted = [...arr].sort((a, b) => a - b)
    const mid = Math.floor(sorted.length / 2)
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
  }
}

function computeJitter(pitchHistory) {
  if (pitchHistory.length < 2) return 0
  const diffs = []
  for (let i = 1; i < pitchHistory.length; i++) {
    if (pitchHistory[i - 1] > 0 && pitchHistory[i] > 0) {
      diffs.push(Math.abs(pitchHistory[i] - pitchHistory[i - 1]))
    }
  }
  return diffs.length ? np.mean(diffs) / (np.mean(pitchHistory) + 1e-6) : 0
}

function computeShimmer(ampHistory) {
  if (ampHistory.length < 2) return 0
  const diffs = []
  for (let i = 1; i < ampHistory.length; i++) {
    diffs.push(Math.abs(ampHistory[i] - ampHistory[i - 1]))
  }
  const meanAmp = np.mean(ampHistory)
  return meanAmp > 0 ? np.mean(diffs) / meanAmp : 0
}

function processAudio(buffer, sampleRate = 16000, timestamp) {
  // Meyda extract expects a buffer, sample rate, and feature list
  try {
    const features = extract(buffer, {
      sampleRate,
      features: ['mfcc', 'pitch', 'loudness', 'spectralFlatness']
    })

    // Collect pitch and loudness history
    PITCH_HISTORY.push(features.pitch || 0)
    AMPLITUDE_HISTORY.push(features.loudness || 0)

    if (PITCH_HISTORY.length > HISTORY_SIZE) PITCH_HISTORY.shift()
    if (AMPLITUDE_HISTORY.length > HISTORY_SIZE) AMPLITUDE_HISTORY.shift()

    const jitter = computeJitter(PITCH_HISTORY)
    const shimmer = computeShimmer(AMPLITUDE_HISTORY)

    // Normalize MFCCs to [0, 1] range roughly
    const mfccNorm = (features.mfcc || Array(13).fill(0)).map(v => Math.max(-1, Math.min(1, v)))

    self.postMessage({
      type: 'result',
      mfcc: mfccNorm,
      pitch: features.pitch || 0,
      loudness: features.loudness || 0,
      jitter,
      shimmer,
      spectralFlatness: features.spectralFlatness || 0,
      timestamp
    })
  } catch (err) {
    console.error('[VoiceWorker] extract failed:', err)
    self.postMessage({ type: 'error', message: err.message })
  }
}

self.onmessage = (event) => {
  const { type, buffer, sampleRate, timestamp } = event.data

  if (type === 'audio') {
    processAudio(buffer, sampleRate || 16000, timestamp || performance.now())
  } else if (type === 'close') {
    self.close()
  }
}

self.postMessage({ type: 'ready' })
console.log('[VoiceWorker] initialized (Meyda extract)')
