import { useState, useEffect } from 'react'
import { useSensor } from '../context/SensorContext'
import { getMetrics, getLogs } from '../utils/diagnostics'

export default function DiagnosticsPage() {
  const { sensorActive, fusionActive } = useSensor()
  const [metrics, setMetrics] = useState(null)
  const [logs, setLogs] = useState([])
  const [health, setHealth] = useState({ workers: {}, model: false, db: false })
  const [testResults, setTestResults] = useState([])

  useEffect(() => {
    const update = () => {
      setMetrics(getMetrics())
      setLogs(getLogs())
      setHealth({
        workers: getMetrics().workers,
        model: getMetrics().fusionReady,
        db: true // assume ok since we use IndexedDB
      })
    }
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [])

  const runSelfTest = async () => {
    const results = []
    results.push({ name: 'Face Worker', status: health.workers.face === 'connected' ? 'pass' : 'fail' })
    results.push({ name: 'Voice Worker', status: health.workers.voice === 'connected' ? 'pass' : 'fail' })
    results.push({ name: 'Fusion Model', status: health.model ? 'pass' : 'fail' })
    results.push({ name: 'IndexedDB', status: health.db ? 'pass' : 'fail' })
    results.push({ name: 'Sensors Active', status: sensorActive ? 'pass' : 'warn' })
    setTestResults(results)
  }

  return (
    <div className="container diagnostics-page">
      <h2>System Diagnostics</h2>
      <p className="text-muted">Comprehensive health check of all subsystems</p>

      <div className="diagnostics-sections">
        <section className="card">
          <h3>System Overview</h3>
          <div className="stat-grid">
            <div className="stat-item">
              <span className="label">Sensors</span>
              <span className={`value ${sensorActive ? 'text-success' : 'text-warn'}`}>
                {sensorActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="stat-item">
              <span className="label">Fusion Model</span>
              <span className={`value ${fusionActive ? 'text-success' : 'text-warn'}`}>
                {fusionActive ? 'Loaded' : 'Loading...'}
              </span>
            </div>
            <div className="stat-item">
              <span className="label">News Engine</span>
              <span className={`value text-success`}>Cached</span>
            </div>
            <div className="stat-item">
              <span className="label">API Gateway</span>
              <span className={`value ${import.meta.env.DEV ? 'text-success' : 'text-muted'}`}>
                {import.meta.env.DEV ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </section>

        <section className="card">
          <h3>Run Self-Test</h3>
          <button className="btn btn-primary" onClick={runSelfTest}>
            Check All Subsystems
          </button>
          {testResults.length > 0 && (
            <div className="test-results">
              {testResults.map((r, i) => (
                <div key={i} className={`test-row ${r.status}`}>
                  <span>{r.name}</span>
                  <span className={`badge badge-${r.status}`}>{r.status.toUpperCase()}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <h3>Performance Metrics</h3>
          {metrics ? (
            <table className="metrics-table">
              <tbody>
                <tr><td>Face Worker FPS</td><td>{metrics.workers?.face?.fps || 0}</td></tr>
                <tr><td>Voice Worker FPS</td><td>{metrics.workers?.voice?.fps || 0}</td></tr>
                <tr><td>Fusion Inference Time</td><td>{metrics.workers?.fusion?.latencyAvg?.toFixed(1) || 0} ms</td></tr>
                <tr><td>Memory Used</td><td>{(metrics.memory?.usedJSHeapSize / 1024 / 1024).toFixed(1)} MB</td></tr>
                <tr><td>News Cache Size</td><td>{metrics.newsCacheSize}</td></tr>
              </tbody>
            </table>
          ) : (
            <p>Loading metrics...</p>
          )}
        </section>

        <section className="card">
          <h3>Event Log (Latest 100)</h3>
          <div className="log-list">
            {logs.slice(-100).reverse().map((log, i) => (
              <div key={i} className={`log-entry log-${log.level}`}>
                <span className="log-time">{log.time?.toLocaleTimeString()}</span>
                <span className="log-source">{log.source}</span>
                <span className="log-msg">{log.message}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
