import { useState, useContext, useEffect } from 'react'
import { SensorContext } from '../context/SensorContext'
import { clearCache, getCacheSize, exportCacheAsJSON, startPeriodicRefresh } from '../services/newsEngine'
import './Settings.css'

function Settings() {
  const { fusionActive } = useContext(SensorContext)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [gazeSmoothing, setGazeSmoothing] = useState(5)
  const [particleQuality, setParticleQuality] = useState('medium')
  const [cacheSize, setCacheSize] = useState('0 KB')
  const [clearing, setClearing] = useState(false)

  useEffect(() => {
    // Initial news engine start if not already started
    startPeriodicRefresh()
    loadCacheSize()
  }, [])

  const loadCacheSize = async () => {
    const size = await getCacheSize()
    setCacheSize(size)
  }

  const handleClearCache = async () => {
    setClearing(true)
    await clearCache()
    await loadCacheSize()
    setClearing(false)
  }

  const handleVoiceToggle = () => {
    setVoiceEnabled(v => !v)
    // Would integrate with sensor context to enable/disable voice worker
  }

  const handleGazeChange = (e) => {
    setGazeSmoothing(e.target.value)
    // Could be passed to face worker for smoothing factor via postMessage
  }

  const handleQualityChange = (e) => {
    setParticleQuality(e.target.value)
    // Could dispatch custom event to starfield hook to adjust density
  }

  const handleExportCache = () => {
    exportCacheAsJSON()
  }

  return (
    <div className="container settings-page">
      <h2>Settings</h2>

      <div className="settings-grid">
        <div className="card setting-item">
          <h3 className="text-mono">News Cache</h3>
          <p className="text-muted">
            Cached articles from Hacker News, Dev.to, Reddit. Current size: <strong>{cacheSize}</strong>
          </p>
          <div className="button-group">
            <button
              className="btn btn-outline"
              onClick={handleClearCache}
              disabled={clearing}
            >
              {clearing ? 'Clearing…' : 'Clear Cache'}
            </button>
            <button
              className="btn btn-outline"
              onClick={handleExportCache}
            >
              Export JSON
            </button>
          </div>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Voice Input</h3>
          <p className="text-muted">Enable/disable microphone stress analysis</p>
          <label className="toggle">
            <input
              type="checkbox"
              checked={voiceEnabled}
              onChange={handleVoiceToggle}
            />
            <span>{voiceEnabled ? 'Enabled' : 'Disabled'}</span>
          </label>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Particle Quality</h3>
          <p className="text-muted">Adjust the 3D mindscape detail level</p>
          <select
            className="settings-select"
            value={particleQuality}
            onChange={handleQualityChange}
          >
            <option value="low">Low (fewer particles)</option>
            <option value="medium">Medium</option>
            <option value="high">High (dense starfield)</option>
          </select>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Gaze Smoothing</h3>
          <p className="text-muted">Filter jitter from eye tracking (0 = off, 10 = max)</p>
          <input
            type="range"
            min="0"
            max="10"
            value={gazeSmoothing}
            onChange={handleGazeChange}
            className="slider"
          />
          <span className="slider-value">{gazeSmoothing}</span>
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Fusion Model Status</h3>
          <p className="text-muted">
            Status: <span className={fusionActive ? 'text-success' : 'text-warn'}>
              {fusionActive ? 'Loaded & Active' : 'Not Loaded (placeholder)'}
            </span>
          </p>
          {!fusionActive && (
            <small className="text-muted">
              Train the model: <code>cd training && python train_fusion_model.py</code>
            </small>
          )}
        </div>

        <div className="card setting-item">
          <h3 className="text-mono">Export Session Data</h3>
          <p className="text-muted">Download your current session data (sensors + predictions) as JSON</p>
          <button
            className="btn btn-outline"
            onClick={handleExportCache}
          >
            Export News Cache
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings
