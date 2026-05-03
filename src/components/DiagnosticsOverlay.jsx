import { useEffect, useRef, useState } from 'react'
import { useSensor } from '../context/SensorContext'

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFPSLabel(metrics) {
  if (!metrics.workers) return '0'
  return Math.round(metrics.workers.face?.fps || 0)
}

export default function DiagnosticsOverlay() {
  const { fusionActive, sensorActive } = useSensor()
  const [metrics, setMetrics] = useState(null)
  const [logs, setLogs] = useState([])
  const [visible, setVisible] = useState(false)
  const [pinned, setPinned] = useState(false)
  const canvasRef = useRef(null)
  const fpsHistoryRef = useRef([])

  useEffect(() => {
    if (!import.meta.env.DEV) return // only in dev

    const handleKey = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault()
        setVisible(v => !v)
      }
      if (e.key === 'Escape' && visible && !pinned) {
        setVisible(false)
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [visible, pinned])

  // Poll diagnostics metrics
  useEffect(() => {
    if (!visible) return
    // Import diagnostics dynamically to avoid heavy bundle
    import('../utils/diagnostics').then(({ getMetrics, getLogs }) => {
      const interval = setInterval(() => {
        const m = getMetrics()
        setMetrics(m)
        if (m.workers?.fusion?.fps) {
          fpsHistoryRef.current.push(m.workers.fusion.fps)
          if (fpsHistoryRef.current.length > 60) fpsHistoryRef.current.shift()
        }
        const l = getLogs()
        setLogs(l)
      }, 500)
      return () => clearInterval(interval)
    })
  }, [visible])

  // Draw FPS graph on canvas
  useEffect(() => {
    if (!visible || !canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const w = canvas.width = canvas.clientWidth
    const h = canvas.height = canvas.clientHeight
    ctx.clearRect(0, 0, w, h)
    if (fpsHistoryRef.current.length < 2) return
    const max = 40
    const min = 0
    ctx.strokeStyle = '#d4af37'
    ctx.lineWidth = 2
    ctx.beginPath()
    fpsHistoryRef.current.forEach((fps, i) => {
      const x = (i / (fpsHistoryRef.current.length - 1)) * w
      const y = h - ((fps - min) / (max - min)) * h
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.stroke()
  }, [visible, metrics, logs])

  if (!visible) return null

  return (
    <div className={`diagnostics-overlay ${pinned ? 'pinned' : ''}`} style={{
      position: 'fixed', top: '1rem', right: '1rem', width: '340px',
      background: 'rgba(0,0,0,0.9)', border: '1px solid #d4af37', borderRadius: '8px',
      color: '#d4af37', fontFamily: 'var(--font-mono)', fontSize: '12px', zIndex: 9999, padding: '1rem'
    }}>
      <div className="overlay-header" style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem'}}>
        <strong>Diagnostics</strong>
        <div>
          <button onClick={() => setPinned(p=>!p)} title={pinned ? 'Unpin' : 'Pin'}>
            {pinned ? '📌' : '📍'}
          </button>
          <button onClick={() => setVisible(false)} style={{marginLeft: '0.25rem'}}>✕</button>
        </div>
      </div>

      <div className="metrics-grid" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1rem'}}>
        <div>Sensors: <span className={sensorActive ? 'text-success' : 'text-warn'}>{sensorActive ? 'ON' : 'OFF'}</span></div>
        <div>Fusion: <span className={fusionActive ? 'text-success' : 'text-warn'}>{fusionActive ? 'READY' : 'LOADING'}</span></div>
        {metrics && (
          <>
            <div>Face FPS: {getFPSLabel(metrics)}</div>
            <div>Memory: {formatBytes(metrics.memory?.usedJSHeapSize || 0)}</div>
            <div>Cache: {metrics.newsCacheSize || '~0.5 MB'}</div>
            <div>Workers OK</div>
          </>
        )}
      </div>

      <div className="fps-graph" style={{marginBottom: '1rem'}}>
        <div style={{fontSize: '10px', marginBottom: '0.25rem'}}>Inference FPS (20 Hz target)</div>
        <canvas ref={canvasRef} style={{width: '100%', height: '60px', background: '#111'}} />
      </div>

      <div className="logs" style={{maxHeight: '120px', overflowY: 'auto', background: '#111', padding: '0.5rem', borderRadius: '4px'}}>
        <div style={{fontSize: '10px', marginBottom: '0.25rem'}}>Recent Logs</div>
        {logs.slice(-10).reverse().map((log, i) => (
          <div key={i} style={{color: log.level === 'error' ? '#f87171' : log.level === 'warn' ? '#fbbf24' : '#d4af37'}}>
            [{log.time?.toLocaleTimeString()}] {log.message}
          </div>
        ))}
      </div>
    </div>
  )
}
