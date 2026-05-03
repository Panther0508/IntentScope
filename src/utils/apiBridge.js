// API Bridge – streams latest app state to local dev server via WebSocket
// Only active in development mode (import.meta.env.DEV)

let ws = null
let heartbeat = null
let currentState = null

// Export function to update state from anywhere
export function updateApiState(section, data) {
  if (currentState && currentState[section]) {
    currentState[section] = { ...currentState[section], ...data }
  }
}

export function initApiBridge(setStateFn) {
  if (!import.meta.env.DEV) return () => {}

  console.log('[API Bridge] Connecting to local gateway at ws://localhost:9001')
  ws = new WebSocket('ws://localhost:9001')

  ws.onopen = () => {
    console.log('[API Bridge] Connected – broadcasting state every 100ms')

    // Acquire state from SensorContext via provided getter
    heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN && setStateFn) {
        currentState = setStateFn()
        ws.send(JSON.stringify(currentState))
      }
    }, 100)
  }

  ws.onerror = (err) => console.error('[API Bridge] WS error:', err)
  ws.onclose = () => console.log('[API Bridge] Disconnected')

  // Return cleanup function
  return () => {
    clearInterval(heartbeat)
    if (ws) ws.close()
  }
}
