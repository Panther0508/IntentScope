import { useState, useEffect } from 'react'
import { useSensor } from '../context/SensorContext'
import { loadScenarioFromFile } from '../utils/simulator'
import NewsTicker from '../components/NewsTicker'

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function Playground() {
  const { startSimulation, stopSimulation, simulationActive, simulationInfo } = useSensor()
  const [scenarios, setScenarios] = useState([])
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [currentFrame, setCurrentFrame] = useState(0)
  const [duration, setDuration] = useState(0)

  // Load available scenarios on mount
  useEffect(() => {
    (async () => {
      const names = ['exploring', 'buy_intent', 'deceptive_response']
      const loaded = await Promise.all(
        names.map(async (name) => {
          try {
            const data = await loadScenarioFromFile(name)
            return { name, ...data }
          } catch (e) {
            console.error('Failed to load scenario', name, e)
            return null
          }
        })
      )
      setScenarios(loaded.filter(Boolean))
    })()
  }, [])

  const handlePlay = () => {
    if (!selectedScenario) return
    // We'll pass the frames directly to a local simulator that sits in this component
    // and inject into SensorContext via startSimulation method (which we added)
    startSimulation(selectedScenario)
    setIsPlaying(true)
  }

  const handlePause = () => {
    stopSimulation()
    setIsPlaying(false)
  }

  const handleStop = () => {
    stopSimulation()
    setIsPlaying(false)
    setCurrentFrame(0)
  }

  // Update UI based on simulation info (polling)
  useEffect(() => {
    if (!simulationActive) return
    const timer = setInterval(() => {
      if (simulationInfo) {
        setCurrentFrame(simulationInfo.currentFrame)
        setDuration(simulationInfo.totalFrames * 0.05) // 20 Hz
      }
    }, 100)
    return () => clearInterval(timer)
   }, [simulationActive, simulationInfo])

  return (
    <div className="container playground-page">
      <h2>Sensor Simulator &amp; Replay</h2>
      <p className="text-muted">
        Test IntentScope without a camera/microphone. Load a pre‑recorded scenario and watch the fusion engine react.
      </p>

      <div className="playground-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <h3>Available Scenarios</h3>
          <ul className="scenario-list">
            {scenarios.map(s => (
              <li key={s.name}>
                <button
                  className={`scenario-btn ${selectedScenario?.name === s.name ? 'active' : ''}`}
                  onClick={() => { setSelectedScenario(s); setDuration(s.duration) }}
                >
                  <strong>{s.name.replace('_', ' ').toUpperCase()}</strong>
                  <span>{s.description}</span>
                  <small>{s.frames.length} frames • {s.duration.toFixed(1)}s</small>
                </button>
              </li>
            ))}
          </ul>

          <div className="player-controls">
            <h4>Player</h4>
            <div className="control-row">
              <button className="btn btn-primary" onClick={handlePlay} disabled={!selectedScenario || isPlaying}>
                Play
              </button>
              <button className="btn btn-outline" onClick={handlePause} disabled={!isPlaying}>
                Pause
              </button>
              <button className="btn btn-outline" onClick={handleStop} disabled={!isPlaying}>
                Stop
              </button>
            </div>

            <div className="control-row">
              <label>Speed</label>
              <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))}>
                <option value={0.5}>0.5×</option>
                <option value={1}>1×</option>
                <option value={2}>2×</option>
                <option value={5}>5×</option>
              </select>
            </div>

            <label className="timeline-label">
              {formatTime(currentFrame * 0.05)} / {formatTime(duration)}
            </label>
            <input
              type="range"
              min="0"
              max={duration * 20 || 100}
              value={currentFrame}
              onChange={(e) => {
                const frame = Number(e.target.value)
                setCurrentFrame(frame)
                // Seek would need a more sophisticated playback engine
              }}
              className="timeline-slider"
            />

            {!isPlaying && selectedScenario && (
              <button className="btn btn-outline" style={{marginTop: '1rem'}}>
                Record Live Session
              </button>
            )}
          </div>

          <div className="status-panel">
            <h4>Current Status</h4>
            <p>Mode: <span className={simulationActive ? 'text-success' : 'text-muted'}>{simulationActive ? 'Simulation' : 'Idle'}</span></p>
            {simulationInfo && (
              <p>
                Scenario: <strong>{simulationInfo.name}</strong><br />
                Progress: {currentFrame} / {simulationInfo.totalFrames} frames
              </p>
            )}
          </div>
        </aside>

        {/* Main view – mirrors Dashboard panels */}
        <main className="simulation-view">
          <NewsTicker />
          <div className="panels">
            <div className="card gauge-card">
              <h3>Deception Gauge</h3>
              <div className="gauge-container">
                {/* Placeholder – real gauge component will be imported */}
                <div className="gauge-fake">
                  <div className="gauge-fill" style={{ width: '30%' }}></div>
                </div>
                <span>30%</span>
              </div>
            </div>
            <div className="card intent-card">
              <h3>Intent Probabilities</h3>
              <div className="intent-bars">
                {/* Mock – replace with real from sensor context */}
                <div className="bar-wrap"><span>Exploring</span><div className="bar" style={{width:'25%'}}></div></div>
                <div className="bar-wrap"><span>BuyIntent</span><div className="bar" style={{width:'10%'}}></div></div>
                <div className="bar-wrap"><span>Hesitation</span><div className="bar" style={{width:'5%'}}></div></div>
                <div className="bar-wrap"><span>Deception</span><div className="bar" style={{width:'2%'}}></div></div>
                <div className="bar-wrap"><span>ActionConfirm</span><div className="bar" style={{width:'15%'}}></div></div>
                <div className="bar-wrap"><span>RobotPick</span><div className="bar" style={{width:'20%'}}></div></div>
                <div className="bar-wrap"><span>RobotPlace</span><div className="bar" style={{width:'8%'}}></div></div>
                <div className="bar-wrap"><span>RobotIdle</span><div className="bar" style={{width:'15%'}}></div></div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
