/**
 * Sensor Aggregator
 * Collects streams from face, voice, and keyboard modules, aligns them by timestamp,
 * maintains a sliding window of timesteps, and produces the 29-feature vector
 * expected by the fusion model.
 */

const FEATURE_DIM = 29

class SensorAggregator {
  constructor(windowSize = 50) {
    this.windowSize = windowSize
    this.buffer = []  // each entry: { timestamp, face, voice, keyboard }
    this.listeners = []

    // Feature normalization ranges (learned from training data – using rough approximations)
    this.normalize = {
      // AUs: [0, 1] already
      gaze: { min: 0, max: 1 },
      mfcc: { min: -1, max: 1 },
      pitch: { min: 80, max: 500 },
      loudness: { min: 0, max: 1 },
      jitter: { min: 0, max: 0.1 },
      shimmer: { min: 0, max: 0.2 },
      interKeyInterval: { min: 30, max: 1000 },
      holdDuration: { min: 20, max: 1000 },
      keyVariance: { min: 0, max: 100 },
      typingSpeed: { min: 0, max: 10 }
    }
  }

  /**
   * Push a new data point into the buffer.
   * @param {Object} data - { face: {...}, voice: {...}, keyboard: {...}, timestamp }
   */
  push(data) {
    this.buffer.push(data)

    // Trim to window size
    if (this.buffer.length > this.windowSize) {
      this.buffer.shift()
    }

    this._notifyListeners()
  }

  /**
   * Subscribe to buffer updates.
   * @param {(buffer: Array, vector: Float32Array) => void} listener
   */
  subscribe(listener) {
    this.listeners.push(listener)
    // Call immediately with current state
    listener(this.buffer, this.getLatestVector())
  }

  /**
   * Convert the most recent timestep into a 29-element feature vector.
   * Fills missing modalities with defaults (zeros or mean values).
   * @returns {Float32Array} 29-element feature vector
   */
  getLatestVector() {
    if (this.buffer.length === 0) {
      return new Float32Array(FEATURE_DIM).fill(0)
    }

    const latest = this.buffer[this.buffer.length - 1]

    // Helper: safe access with default
    const safe = (obj, key, defaultVal) => (obj && obj[key] !== undefined) ? obj[key] : defaultVal

    // 1. Face AUs (6)
    const au = latest.face?.au || {}
    const au1 = safe(au, 'AU1', 0)
    const au2 = safe(au, 'AU2', 0)
    const au12 = safe(au, 'AU12', 0)
    const au15 = safe(au, 'AU15', 0)
    const au20 = safe(au, 'AU20', 0)
    const au26 = safe(au, 'AU26', 0)

    // 2. Gaze (2)
    const gazeX = safe(latest.face, 'gaze_x', 0.5)
    const gazeY = safe(latest.face, 'gaze_y', 0.5)

    // 3. Voice features (MFCC 13 + pitch + loudness + jitter + shimmer)
    const voice = latest.voice || {}
    const mfcc = Array.isArray(voice.mfcc)
      ? voice.mfcc.slice(0, 13).map(v => Math.max(-1, Math.min(1, v)))
      : Array(13).fill(0)
    const pitch = safe(voice, 'pitch', 200)
    const loudness = safe(voice, 'loudness', 0.3)
    const jitter = safe(voice, 'jitter', 0.01)
    const shimmer = safe(voice, 'shimmer', 0.02)

    // 4. Keyboard stats (4)
    const kb = latest.keyboard || {}
    const interKeyInterval = safe(kb, 'interKeyInterval', 200)
    const holdDuration = safe(kb, 'holdDuration', 100)
    const variance = safe(kb, 'variance', 20)
    const typingSpeed = safe(kb, 'typingSpeed', 2)

    // Assemble vector (must match training order)
    const vec = new Float32Array([
      // Action Units (0-5)
      au1, au2, au12, au15, au20, au26,
      // Gaze (6-7)
      gazeX, gazeY,
      // MFCC (8-20)
      ...mfcc,
      // Audio extras (21-24)
      pitch, loudness, jitter, shimmer,
      // Keyboard (25-28)
      interKeyInterval, holdDuration, variance, typingSpeed
    ])

    return vec
  }

   /**
    * Get a multi-timestep tensor for model input.
    * @returns {Float32Array} shape (1, windowSize, FEATURE_DIM) ready for ONNX
    */
   getTensorInput() {
     const frames = this.buffer.length
     if (frames < this.windowSize) {
       // Pad with zeros at the beginning; tensor has windowSize timesteps
       const tensor = new Float32Array(this.windowSize * FEATURE_DIM)
       const startOffset = (this.windowSize - frames) * FEATURE_DIM
       for (let i = 0; i < frames; i++) {
         const entry = this.buffer[i]
         const vec = this._vectorFromEntry(entry)
         tensor.set(vec, startOffset + i * FEATURE_DIM)
       }
       return tensor
     }

     // Buffer is full: fill entire tensor
     const tensor = new Float32Array(this.windowSize * FEATURE_DIM)
     for (let i = 0; i < this.windowSize; i++) {
       const entry = this.buffer[i]
       const vec = this._vectorFromEntry(entry)
       tensor.set(vec, i * FEATURE_DIM)
     }
     return tensor
   }

  _vectorFromEntry(entry) {
    const safe = (obj, key, defaultVal) => (obj && obj[key] !== undefined) ? obj[key] : defaultVal
    const au = entry.face?.au || {}
    const mfcc = Array.isArray(entry.voice?.mfcc) ? entry.voice.mfcc.slice(0, 13) : Array(13).fill(0)
    return new Float32Array([
      safe(au, 'AU1', 0), safe(au, 'AU2', 0), safe(au, 'AU12', 0),
      safe(au, 'AU15', 0), safe(au, 'AU20', 0), safe(au, 'AU26', 0),
      safe(entry.face, 'gaze_x', 0.5), safe(entry.face, 'gaze_y', 0.5),
      ...mfcc,
      safe(entry.voice, 'pitch', 200), safe(entry.voice, 'loudness', 0.3),
      safe(entry.voice, 'jitter', 0.01), safe(entry.voice, 'shimmer', 0.02),
      safe(entry.keyboard, 'interKeyInterval', 200),
      safe(entry.keyboard, 'holdDuration', 100),
      safe(entry.keyboard, 'variance', 20),
      safe(entry.keyboard, 'typingSpeed', 2)
    ])
  }

  /**
   * Get current buffer fill level.
   */
  getFillLevel() {
    return this.buffer.length
  }

  _notifyListeners() {
    const vector = this.getLatestVector()
    for (const listener of this.listeners) {
      listener(this.buffer, vector)
    }
  }

  /**
   * Reset buffer to empty.
   */
  reset() {
    this.buffer = []
    this._notifyListeners()
  }
}

export default SensorAggregator
