function Dashboard() {
  return (
    <div className="container">
      <h2>Live Dashboard</h2>

      <div className="dashboard-grid">
        {/* Top row */}
        <div className="card">
          <h3 className="text-mono">Face Feed</h3>
          <div className="sensor-placeholder">
            <div className="shimmer"></div>
            <span>Webcam feed with face mesh overlay</span>
          </div>
        </div>

        <div className="card">
          <h3 className="text-mono">Intent Prediction</h3>
          <div className="prediction-placeholder">
            <div className="shimmer"></div>
            <p className="text-gold">No prediction yet</p>
            <div className="confidence-bar">
              <div className="bar-fill" style={{ width: '0%' }}></div>
            </div>
          </div>
        </div>

        {/* Middle row */}
        <div className="card">
          <h3 className="text-mono">Voice Stress Meter</h3>
          <div className="meter-bars">
            {[40, 65, 30, 85, 50].map((height, i) => (
              <div key={i} className="bar" style={{ height: `${height}%` }}></div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="text-mono">Keyboard Dynamics</h3>
          <div className="key-stats">
            <p>Keystrokes: <span className="text-gold">0</span></p>
            <p>Avg Dwell: <span className="text-gold">0 ms</span></p>
            <p>Flight Time: <span className="text-gold">0 ms</span></p>
          </div>
        </div>

        {/* Bottom row */}
        <div className="card robot-mini">
          <h3 className="text-mono">Robotic Arm – Quick View</h3>
          <div className="dashed-box">Robot Lab Quick View</div>
        </div>

        <div className="card narrator-snippet">
          <h3 className="text-mono">AI Narrator Snippet</h3>
          <div className="terminal">
            <p><span className="prompt">&gt;</span> Initializing...</p>
            <p><span className="prompt">&gt;</span> Waiting for sensor data...</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
