import { useState } from 'react'

export default function ApiPlayground() {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const gatewayActive = import.meta.env.DEV

  const endpoints = [
    { name: 'Sensors', path: '/api/sensors' },
    { name: 'Intent', path: '/api/intent' },
    { name: 'Narration', path: '/api/narration' },
    { name: 'Robot', path: '/api/robot' },
    { name: 'Status', path: '/api/status' }
  ]

  const tryEndpoint = async (path) => {
    setLoading(true)
    setError(null)
    setResponse(null)
    try {
      const resp = await fetch(path)
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      setResponse(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container api-playground-page">
      <h2>🛠 API Playground</h2>
      <p className="text-muted">
        During development, IntentScope exposes a local API on <code>http://localhost:3000</code> that mirrors live sensor state.
        Use it from your terminal or any HTTP client.
      </p>

      {!gatewayActive ? (
        <div className="alert alert-info">
          The Local API Gateway is only available when running <code>npm run dev</code>.
          It is disabled in production builds.
        </div>
      ) : (
        <>
          <div className="endpoint-grid">
            {endpoints.map(ep => (
              <div key={ep.path} className="card endpoint-card">
                <h4>{ep.name}</h4>
                <code className="endpoint-path">{ep.path}</code>
                <pre className="curl-example">curl {ep.path}</pre>
                <button className="btn btn-outline btn-sm" onClick={() => tryEndpoint(ep.path)}>
                  Try it
                </button>
              </div>
            ))}
          </div>

          <div className="response-area">
            <h3>Response</h3>
            {loading && <p>Loading…</p>}
            {error && <pre className="error">{error}</pre>}
            {response && (
              <pre className="json-output">
                {JSON.stringify(response, null, 2)}
              </pre>
            )}
          </div>
        </>
      )}

      <div className="api-info card">
        <h3>📖 How to Use</h3>
        <p>From a terminal (in another window), run:</p>
        <pre className="bash-example">
{`# Terminal – while app is running
curl http://localhost:3000/api/intent | jq .topIntent`}
        </pre>
        <p>Or use Postman / Thunder Client (VS Code) to query the endpoints live while you interact with the app.</p>
        <p><strong>Note:</strong> The API only works in the same origin (localhost:3000) due to CORS policy during dev.</p>
      </div>
    </div>
  )
}
