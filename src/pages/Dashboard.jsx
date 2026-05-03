import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSensor } from '../context/SensorContext'

function Dashboard() {
  const {
    sensorActive,
    sensorError,
    faceData,
    voiceData,
    keyboardData,
    bufferFill,
    startSensors,
    stopSensors,
    getLatestVector
  } = useSensor()

  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [prediction, setPrediction] = useState({ label: null, confidence: 0 })

  // Draw webcam with gaze overlay
  useEffect(() => {
    if (!sensorActive || !videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    const draw = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        ctx.drawImage(video, 0, 0)

        // Draw gaze dot
        if (faceData && faceData.gaze_x !== undefined) {
          const x = faceData.gaze_x * canvas.width
          const y = faceData.gaze_y * canvas.height

          ctx.beginPath()
          ctx.arc(x, y, 12, 0, Math.PI * 2)
          ctx.fillStyle = '#D4AF37'  // gold
          ctx.shadowColor = '#D4AF37'
          ctx.shadowBlur = 15
          ctx.fill()
          ctx.shadowBlur = 0

          // Crosshairs
          ctx.strokeStyle = 'rgba(212, 175, 55, 0.6)'
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(x - 20, y)
          ctx.lineTo(x + 20, y)
          ctx.moveTo(x, y - 20)
          ctx.lineTo(x, y + 20)
          ctx.stroke()
        }
      }
      requestAnimationFrame(draw)
    }

    draw()
  }, [sensorActive, faceData])

  // Predict intent periodically when buffer has data
  useEffect(() => {
    if (bufferFill >= 50 && getLatestVector) {
      // Placeholder prediction – in Phase 3 we'll load ONNX model
      const vector = getLatestVector()
      // Dummy: pick class based on high AU12 (smile) or high AU26 (jaw drop)
      const au12 = vector[2]
      const au26 = vector[5]
      let label = 'Exploring'
      let confidence = 25
      if (au12 > 0.6) { label = 'BuyIntent'; confidence = 90 }
      else if (au26 > 0.5) { label = 'Deception'; confidence = 75 }
      else if (vector[25] < 100) { label = 'Hesitation'; confidence = 60 }
      setPrediction({ label, confidence })
    }
  }, [bufferFill, getLatestVector])

  return (
    <div className="container">
      <div className="dashboard-header">
        <h2>Live Dashboard</h2>
        <div className="control-buttons">
          {sensorActive ? (
            <button className="btn btn-outline" onClick={stopSensors}>Stop Sensors</button>
          ) : (
            <button className="btn btn-gold" onClick={startSensors}>Start Sensors</button>
          )}
        </div>
      </div>

      {sensorError && (
        <div className="error-banner card" style={{ marginBottom: '1.5rem', color: '#ff4d4d' }}>
          {sensorError}
        </div>
      )}

      <div className="dashboard-grid">
        {/* Top row */}
        <div className="card">
          <h3 className="text-mono">Face Feed</h3>
          <div className="video-wrapper">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              style={{ display: sensorActive ? 'block' : 'none' }}
            />
            <canvas ref={canvasRef} className="gaze-canvas" />
            {!sensorActive && (
              <div className="sensor-placeholder">
                <div className="shimmer"></div>
                <span>Webcam feed with face mesh overlay</span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-mono">Intent Prediction</h3>
          <div className="prediction-content">
            <p className="prediction-label">
              {prediction.label
                ? <span className="text-gold">{prediction.label}</span>
                : <span className="text-muted">Waiting for data...</span>}
            </p>
            <div className="confidence-bar">
              <div className="bar-fill" style={{ width: `${prediction.confidence}%` }}></div>
            </div>
            <p className="buffer-status">
              Buffer: {bufferFill} / 50 timesteps
            </p>
          </div>
        </div>

        {/* Middle row */}
        <div className="card">
          <h3 className="text-mono">Voice Stress Meter</h3>
          <div className="meter-bars">
            {voiceData ? (
              <>
                <div className="meter-bar" title="Pitch">
                  <div className="meter-fill" style={{ height: `${Math.min(100, (voiceData.pitch / 300) * 100)}%` }}></div>
                  <span>{Math.round(voiceData.pitch)} Hz</span>
                </div>
                <div className="meter-bar" title="Jitter">
                  <div className="meter-fill" style={{ height: `${Math.min(100, voiceData.jitter * 1000)}%` }}></div>
                  <span>J: {(voiceData.jitter * 100).toFixed(2)}%</span>
                </div>
                <div className="meter-bar" title="Shimmer">
                  <div className="meter-fill" style={{ height: `${Math.min(100, voiceData.shimmer * 1000)}%` }}></div>
                  <span>S: {(voiceData.shimmer * 100).toFixed(2)}%</span>
                </div>
              </>
            ) : (
              <span className="text-muted">No voice data</span>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-mono">Keyboard Dynamics</h3>
          <div className="key-stats">
            {keyboardData ? (
              <>
                <p>Interval: <span className="text-gold">{Math.round(keyboardData.interKeyInterval)} ms</span></p>
                <p>Hold: <span className="text-gold">{Math.round(keyboardData.holdDuration)} ms</span></p>
                <p>Variance: <span className="text-gold">{Math.round(keyboardData.variance)}</span></p>
              </>
            ) : (
              <>
                <p>Interval: <span className="text-gold">—</span></p>
                <p>Hold: <span className="text-gold">—</span></p>
                <p>Variance: <span className="text-gold">—</span></p>
              </>
            )}
          </div>
        </div>

        {/* Bottom row */}
        <div className="card robot-mini">
          <h3 className="text-mono">Robotic Arm – Quick View</h3>
          <Link to="/robot" className="btn btn-outline">Open Robot Lab →</Link>
        </div>

        <div className="card narrator-snippet">
          <h3 className="text-mono">AI Narrator Snippet</h3>
          <div className="terminal">
            <p><span className="prompt">&gt;</span> {sensorActive ? 'Sensors active...' : 'Sensors idle.'}</p>
            <p><span className="prompt">&gt;</span> {prediction.label ? `Intent: ${prediction.label}` : 'Awaiting prediction...'}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
