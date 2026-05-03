/**
 * Dev State Store – Shared mutable state for local API bridge
 * This module is only used in development mode.
 * Provides a simple publish-subscribe store for sensor/intent/robot/narration state.
 */

const state = {
  sensors: {
    faceData: null,
    voiceData: null,
    keyboardData: null,
    bufferFill: 0,
    sensorActive: false
  },
  intent: {
    intentProbabilities: {},
    topIntent: null,
    confidence: 0,
    deceptionProbability: 0
  },
  narration: {
    latestNarration: '',
    lastUpdated: null
  },
  robot: {
    currentAction: 'idle',
    target: null,
    jointAngles: [],
    mode: 'intent'
  },
  status: {
    sensorsActive: false,
    fusionReady: false,
    usingSimulation: false,
    newsCacheSize: '0 B'
  }
}

// Subscribers (e.g., bridge)
const subscribers = new Set()

/**
 * Update state with a partial patch object
 * @param {Object} patch - May contain sensors/intent/narration/robot/status keys with partial objects
 */
export function updateDevState(patch) {
  if (patch.sensors) Object.assign(state.sensors, patch.sensors)
  if (patch.intent) Object.assign(state.intent, patch.intent)
  if (patch.narration) Object.assign(state.narration, patch.narration)
  if (patch.robot) Object.assign(state.robot, patch.robot)
  if (patch.status) Object.assign(state.status, patch.status)

  // Notify subscribers
  for (const sub of subscribers) {
    try {
      sub(state)
    } catch (err) {
      console.error('[DevStateStore] Subscriber error:', err)
    }
  }
}

/**
 * Get a deep copy of the current state
 */
export function getDevState() {
  return JSON.parse(JSON.stringify(state))
}

/**
 * Subscribe to state changes; returns unsubscribe function
 */
export function subscribe(callback) {
  subscribers.add(callback)
  // Immediately invoke with current state
  callback(state)
  return () => subscribers.delete(callback)
}

/**
 * Set a specific field (convenience)
 */
export function setSensors(sensors) { updateDevState({ sensors }) }
export function setIntent(intent) { updateDevState({ intent }) }
export function setNarration(narration) { updateDevState({ narration }) }
export function setRobot(robot) { updateDevState({ robot }) }
export function setStatus(status) { updateDevState({ status }) }
