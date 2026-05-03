function Analysis() {
  return (
    <div className="container">
      <h2>Live Analysis</h2>

      <div className="analysis-layout">
        {/* Face mesh area */}
        <div className="card analysis-main">
          <h3 className="text-mono">Face Mesh Overlay</h3>
          <div className="sensor-placeholder large">
            <div className="shimmer"></div>
            <span>Real-time webcam feed with 468 facial landmarks</span>
          </div>
        </div>

        {/* Right side log panel */}
        <div className="card analysis-log">
          <h3 className="text-mono">Sensor Data Stream</h3>
          <div className="log-stream">
            <p><span className="log-time">[00:00:00]</span> System initialized...</p>
            <p><span className="log-time">[00:00:01]</span> Waiting for camera...</p>
            <p><span className="log-time">[00:00:02]</span> Microphone ready...</p>
            <p><span className="text-muted">Log lines will appear here...</span></p>
          </div>
        </div>
      </div>

      {/* Toggle buttons (non-functional) */}
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
