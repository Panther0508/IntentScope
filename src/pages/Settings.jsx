function Settings() {
  return (
    <div className="container settings-page">
      <h2>Settings</h2>

      <div className="settings-grid">
        <div className="card setting-item">
          <h3 className="text-mono">Model Cache</h3>
          <p className="text-muted">Manage downloaded ONNX and LLM models</p>
          <button className="btn btn-outline">Clear Cache</button>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Voice Input</h3>
          <p className="text-muted">Enable/disable microphone stress analysis</p>
          <label className="toggle">
            <input type="checkbox" defaultChecked />
            <span>Enabled</span>
          </label>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Particle Quality</h3>
          <p className="text-muted">Adjust the 3D mindscape detail level</p>
          <select className="settings-select">
            <option>Low</option>
            <option selected>Medium</option>
            <option>High</option>
          </select>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Gaze Smoothing</h3>
          <p className="text-muted">Filter jitter from eye tracking</p>
          <input type="range" min="0" max="10" defaultValue="5" className="slider" />
        </div>
      </div>
    </div>
  )
}

export default Settings
