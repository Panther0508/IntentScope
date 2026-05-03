function DeceptionChallenge() {
  return (
    <div className="container deception-page">
      <h2>Deception Challenge</h2>

      <div className="challenge-layout">
        {/* Question */}
        <div className="card question-card">
          <h3 className="text-mono">Question</h3>
          <p className="question-text">"Did you take the last cookie from the jar?"</p>
        </div>

        {/* Webcam */}
        <div className="card camera-card">
          <h3 className="text-mono">Live Feed</h3>
          <div className="sensor-placeholder">
            <div className="shimmer"></div>
            <span>Camera will activate during challenge</span>
          </div>
        </div>

        {/* Controls */}
        <div className="controls">
          <button className="btn btn-gold">Start Challenge</button>
          <button className="btn btn-outline">Reset</button>
        </div>

        {/* Scoreboard */}
        <div className="card scoreboard">
          <h3 className="text-mono">Score</h3>
          <div className="score-item">
            <span>Truth Detection:</span>
            <span className="text-gold">—</span>
          </div>
          <div className="score-item">
            <span>Confidence:</span>
            <span className="text-gold">—</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DeceptionChallenge
