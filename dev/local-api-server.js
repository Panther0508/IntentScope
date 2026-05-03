const WebSocket = require('ws')
const http = require('http')
const url = require('url')

const PORT = process.env.INTENTSCOPE_API_PORT || 9001

// Store latest state snapshot (updated by WebSocket clients)
let latestState = {
  sensors: { faceData: null, voiceData: null, keyboardData: null, bufferFill: 0, sensorActive: false },
  intent: { intentProbabilities: null, topIntent: null, confidence: 0, deceptionProbability: 0 },
  narration: { latestNarration: '', lastUpdated: null },
  robot: { currentAction: 'idle', target: null, jointAngles: [], mode: 'intent' },
  status: { sensorsActive: false, fusionReady: false, usingSimulation: false, newsCacheSize: '0 KB' }
}

// WebSocket server for pushing state FROM browser TO Node
const wss = new WebSocket.Server({ port: PORT })
wss.on('connection', (ws) => {
  console.log(`[LocalAPI] Browser connected on port ${PORT}`)

  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg)
      // Merge state
      latestState = { ...latestState, ...data }
    } catch (e) { console.error('[LocalAPI] Invalid message:', e) }
  })

  ws.on('close', () => console.log('[LocalAPI] Browser disconnected'))
})

console.log(`[LocalAPI] WebSocket server listening on port ${PORT}`)

// HTTP server for /api/* endpoints
const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url)
  if (parsed.pathname?.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json')
    res.setHeader('Access-Control-Allow-Origin', '*')

    const endpoint = parsed.pathname

    switch (endpoint) {
      case '/api/sensors':
        res.end(JSON.stringify(latestState.sensors))
        break
      case '/api/intent':
        res.end(JSON.stringify(latestState.intent))
        break
      case '/api/narration':
        res.end(JSON.stringify(latestState.narration))
        break
      case '/api/robot':
        res.end(JSON.stringify(latestState.robot))
        break
      case '/api/status':
        res.end(JSON.stringify(latestState.status))
        break
      default:
        res.statusCode = 404
        res.end(JSON.stringify({ error: 'Not found' }))
    }
  } else {
    // Not an API endpoint – ignore (Vite handles it)
    res.end('')
  }
})

server.listen(PORT, () => {
  console.log(`[LocalAPI] HTTP proxy listening on port ${PORT}`)
})
