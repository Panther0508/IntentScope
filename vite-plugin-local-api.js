import { spawn } from 'child_process'
import { resolve } from 'path'

export default function localApiGateway() {
  let serverProcess = null

  return {
    name: 'local-api-gateway',
    configureServer(server) {
      // Only start in dev
      if (process.env.NODE_ENV !== 'development') return

      const serverPath = resolve(__dirname, 'dev/local-api-server.js')
      serverProcess = spawn('node', [serverPath], {
        detached: true,
        stdio: 'inherit',
        env: { ...process.env, INTENTSCOPE_API_PORT: '9001' }
      })

      serverProcess.unref()

      // Proxy /api/* to our local server
      server.middlewares.use((req, res, next) => {
        if (req.url?.startsWith('/api/')) {
          const http = require('http')
          const options = {
            hostname: 'localhost',
            port: 9001,
            path: req.url,
            method: 'GET'
          }
          const proxy = http.request(options, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers)
            proxyRes.pipe(res)
          })
          proxy.on('error', () => next())
          proxy.end()
        } else {
          next()
        }
      })

      console.log('[Vite plugin] Local API Gateway started on http://localhost:9001')
    },
    closeServer() {
      if (serverProcess) {
        serverProcess.kill('SIGTERM')
        serverProcess = null
      }
    }
  }
}
