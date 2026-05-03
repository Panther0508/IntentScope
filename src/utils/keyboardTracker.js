/**
 * Keyboard Dynamics Tracker
 * Listens to keydown/keyup events and computes typing statistics.
 *
 * Exposes: initKeyboardTracker(callback) → returns stop function
 *
 * Callback receives:
 *   { interKeyInterval, holdDuration, variance, timestamp }
 */

let lastKeyDownTime = 0
let lastKeyUpTime = 0
let currentKeyDownTime = 0
const recentIntervals = []
const recentHoldDurations = []
const WINDOW_SIZE = 10

/**
 * Initialize keyboard event listeners.
 * @param {(data: {interKeyInterval:number, holdDuration:number, variance:number, timestamp:number}) => void} callback
 * @returns {() => void} cleanup function
 */
export function initKeyboardTracker(callback) {
  const computeStats = (arr) => {
    if (arr.length < 2) return 0
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length
    const variance = arr.reduce((s, v) => s + (v - mean) ** 2, 0) / arr.length
    return variance
  }

  const handleKeyDown = (e) => {
    const now = performance.now()

    // Compute inter-key interval if we have previous timestamp
    if (lastKeyDownTime > 0) {
      const interval = now - lastKeyDownTime
      recentIntervals.push(interval)
      if (recentIntervals.length > WINDOW_SIZE) recentIntervals.shift()
    }

    currentKeyDownTime = now
    lastKeyDownTime = now
  }

  const handleKeyUp = (e) => {
    const now = performance.now()

    if (currentKeyDownTime > 0) {
      const holdDuration = now - currentKeyDownTime
      recentHoldDurations.push(holdDuration)
      if (recentHoldDurations.length > WINDOW_SIZE) recentHoldDurations.shift()
    }

    // Emit stats on key release (the event is complete)
    const interKeyInterval = recentIntervals.length ? recentIntervals[recentIntervals.length - 1] : 0
    const holdDuration = recentHoldDurations.length ? recentHoldDurations[recentHoldDurations.length - 1] : 0
    const intervalVariance = computeStats(recentIntervals)

    callback({
      interKeyInterval,
      holdDuration,
      variance: intervalVariance,
      timestamp: now
    })

    lastKeyUpTime = now
    currentKeyDownTime = 0
  }

  // Attach listeners
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)

  console.log('[KeyboardTracker] initialized')

  // Return cleanup function
  return () => {
    window.removeEventListener('keydown', handleKeyDown)
    window.removeEventListener('keyup', handleKeyUp)
    console.log('[KeyboardTracker] stopped')
  }
}

// Export stop function separately if needed
export function stopKeyboardTracker() {
  // This is just a placeholder – use the cleanup closure
  console.log('[KeyboardTracker] use cleanup() returned from initKeyboardTracker')
}
