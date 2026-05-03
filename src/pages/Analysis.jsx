import { useEffect, useState } from 'react'
import { useSensor } from '../context/SensorContext'

function Analysis() {
  const { sensorActive, faceData, voiceData, keyboardData, bufferFill, aggregator } = useSensor()
  const [logs, setLogs] = useState([
    { time: new Date(), text: 'System initialized...' },
    { time: new Date(), text: 'Waiting for camera...' },
    { time: new Date(), text: 'Microphone ready...' }
  ])

  // Add a new log entry
  const addLog = (text) => {
    setLogs(prev => [...prev.slice(-49), { time: new Date(), text }])  // keep last 50
  }

  // Subscribe to sensor updates
  useEffect(() => {
    if (!sensorActive) return

    const unsubscribe = aggregator.subscribe((buffer, vector) => {
      // Log at reduced frequency to avoid spam
      if (buffer.length % 10 === 0) {
        const latest = buffer[buffer.length - 1]
        const hasFace = !!latest?.face
        const hasVoice = !!latest?.voice
        const hasKb = !!latest?.keyboard
        addLog(`[T+${buffer.length}] Face:${hasFace ? '✓' : '✗'} Voice:${hasFace ? '✓' : '✗'} KB:${hasKb ? '✓' : '✗'}`)
      }
    })

    return () => unsubscribe()
  }, [sensorActive, aggregator])

  // Format timestamp
  const formatTime = (date) => {
    return date.toTimeString().split(' ')[0]
  }

  return (
    <div className="container">
      <h2>Live Analysis</h2>

      <div className="analysis-layout">
        {/* Face mesh area (simple video) */}
        <div className="card analysis-main">
          <h3 className="text-mono">Sensor Feed</h3>
          {sensorActive && faceData && (
            <div className="live-details">
              <div className="detail-row">
                <span>Gaze X:</span>
                <span className="text-gold">{faceData.gaze_x.toFixed(3)}</span>
              </div>
              <div className="detail-row">
                <span>Gaze Y:</span>
                <span className="text-gold">{faceData.gaze_y.toFixed(3)}</span>
              </div>
              <div className="au-grid">
                {Object.entries(faceData.au).map(([k, v]) => (
                  <div key={k} className="au-item">
                    <span className="au-label">{k}</span>
                    <div className="au-bar-bg">
                      <div className="au-bar-fill" style={{ width: `${v * 100}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {!sensorActive && (
            <div className="sensor-placeholder large">
              <div className="shimmer"></div>
              <span>Start sensors to see live data</span>
            </div>
          )}
        </div>

        {/* Right side log panel */}
        <div className="card analysis-log">
          <div className="log-header">
            <h3 className="text-mono">Sensor Data Stream</h3>
            <span className="buffer-count">Buffer: {bufferFill}/50</span>
          </div>
          <div className="log-stream">
            {logs.map((log, i) => (
              <p key={i}>
                <span className="log-time">[{formatTime(log.time)}]</span> {log.text}
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Toggle buttons (non-functional for now) */}
      <div className="analysis-toggles">
        <button className="btn btn-outline">Face Mesh</button>
        <button className="btn btn-outline">Gaze Vector</button>
        <button className="btn btn-outline">Audio Spectrum</button>
        <button className="btn btn-outline">Raw Log</button>
      </div>
    </div>
  )
}

export default Analysis
