export function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const LOG_BUFFER = []
const MAX_LOGS = 200

let perfMetrics = {
  face: { fps: 0, latencyAvg: 0 },
  voice: { fps: 0, latencyAvg: 0 },
  fusion: { fps: 0, latencyAvg: 0 },
  inferenceStart: null,
  inferenceTimes: []
}

let workersStatus = { face: 'disconnected', voice: 'disconnected', fusion: 'disconnected' }
let memorySnapshot = { usedJSHeapSize: 0 }

export function startMonitoring() {
  // Start 1-second heartbeat to compute FPS
  setInterval(() => {
    // For demo: just mock FPS around 20
    perfMetrics.face.fps = Math.round(18 + Math.random() * 4)
    perfMetrics.voice.fps = Math.round(18 + Math.random() * 4)
    perfMetrics.fusion.fps = Math.round(20)
    perfMetrics.fusion.latencyAvg = 5 + Math.random() * 3

    // Get current memory (Chrome only)
    if (performance.memory) {
      memorySnapshot.usedJSHeapSize = performance.memory.usedJSHeapSize
    }
  }, 1000)
}

export function stopMonitoring() {
  // Nothing to clean up (intervals auto-clear on page unload)
}

export function recordWorkerMessage(_workerName) {
  // Increment message count – used by FPS calculator
  // In a real impl we'd count messages per second; this is minimalist
  // _workerName reserved for future per-worker metrics
}

export function recordInferenceStart() {
  perfMetrics.inferenceStart = performance.now()
}

export function recordInferenceEnd() {
  if (perfMetrics.inferenceStart) {
    const duration = performance.now() - perfMetrics.inferenceStart
    perfMetrics.inferenceTimes.push(duration)
    if (perfMetrics.inferenceTimes.length > 100) perfMetrics.inferenceTimes.shift()
    // Rolling average
    perfMetrics.fusion.latencyAvg = perfMetrics.inferenceTimes.reduce((a,b)=>a+b,0) / perfMetrics.inferenceTimes.length
  }
}

export function updateWorkerStatus(workerName, status) {
  workersStatus[workerName] = status
}

export function logEvent(level, source, message) {
  LOG_BUFFER.push({
    time: new Date(),
    level,
    source,
    message
  })
  if (LOG_BUFFER.length > MAX_LOGS) LOG_BUFFER.shift()
}

export function getMetrics() {
  return {
    workers: { ...perfMetrics.workers } || workersStatus,
    memory: memorySnapshot,
    newsCacheSize: '~0.5 MB' // placeholder (could query IndexedDB)
  }
}

export function getLogs() {
  return [...LOG_BUFFER]
}
