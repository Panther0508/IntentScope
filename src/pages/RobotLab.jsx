import { useState, useEffect } from 'react'
import { useSensor } from '../context/SensorContext'
import { setRobot } from '../utils/devStateStore.js'

function RobotLab() {
  const { fusionActive, fusionResult } = useSensor()
  const [mode, setMode] = useState('intent') // 'intent' | 'expression'
  const [robotState, setRobotState] = useState({ action: 'idle', target: null })

  // Simple state machine for robot behavior based on intent
  useEffect(() => {
    if (!fusionActive || mode !== 'intent') return

    const confidence = fusionResult.confidence
    const deception = fusionResult.deceptionProbability
    const topIntent = fusionResult.intentProbabilities
      ? Object.entries(fusionResult.intentProbabilities).reduce((a, b) => a[1] > b[1] ? a : b)[0]
      : null

    // Deception causes robot to enter "suspicious" posture
    if (deception > 0.6) {
      setRobotState({ action: 'suspend', target: null })
    } else if (topIntent === 'RobotPick' && confidence > 0.7) {
      setRobotState({ action: 'pick', target: 'object_01' })
    } else if (topIntent === 'RobotPlace' && confidence > 0.7) {
      setRobotState({ action: 'place', target: 'bin_01' })
    } else if (topIntent === 'Exploring') {
      setRobotState({ action: 'scan', target: null })
    } else {
      // Default idle with slight movement to show alive
      setRobotState({ action: 'idle', target: null })
    }
  }, [fusionResult, mode, fusionActive])

  // Push robot state to devStateStore (dev-only)
  useEffect(() => {
    if (import.meta.env.DEV) {
      setRobot({
        currentAction: robotState.action,
        target: robotState.target,
        jointAngles: [], // Not tracked in this UI; could be populated if available
        mode: mode
      })
    }
  }, [robotState, mode])

  return (
    <div className="robot-lab">
      <aside className="sidebar glass">
        <h3>Control Mode</h3>
        <div className="mode-toggle">
          <button
            className={`toggle-btn ${mode === 'intent' ? 'active' : ''}`}
            onClick={() => setMode('intent')}
          >
            Mind-Controlled (Intent)
          </button>
          <button
            className={`toggle-btn ${mode === 'expression' ? 'active' : ''}`}
            onClick={() => setMode('expression')}
          >
            Expression-Only
          </button>
        </div>

        <h3>Live Intent</h3>
        {fusionActive && fusionResult ? (
          <div className="intent-list">
            {Object.entries(fusionResult.intentProbabilities).map(([k, v]) => (
              <div key={k} className="intent-bar-row">
                <span>{k}</span>
                <div className="intent-bar-bg">
                  <div className="intent-bar-fill" style={{ width: `${v * 100}%` }}></div>
                </div>
                <span>{Math.round(v * 100)}%</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted">Waiting for fusion...</p>
        )}

        <h3>Current Action</h3>
        <div className="robot-state">
          <span className="state-action">{robotState.action.toUpperCase()}</span>
          {robotState.target && <span className="state-target">{robotState.target}</span>}
        </div>

        {mode === 'expression' && (
          <p className="hint-text text-muted">
            Expression mode uses raw AU/gaze thresholds. Switch to Intent mode for predictive behavior.
          </p>
        )}
      </aside>

      <main className="robot-main">
        <h2>Robotic Arm – {mode === 'intent' ? 'Intent-Driven' : 'Expression-Controlled'}</h2>
        <div id="robot-canvas" className="robot-viewport">
          <div className="robot-placeholder">
            <div className="robot-icon">🤖</div>
            <p className="text-gold">Robot Arm Visualization</p>
            <p className="text-muted">
              {robotState.action === 'idle' && 'Arm idle – think about picking or placing an object'}
              {robotState.action === 'pick' && 'Picking up object...'}
              {robotState.action === 'place' && 'Placing held object...'}
              {robotState.action === 'scan' && 'Scanning environment...'}
              {robotState.action === 'suspend' && '⚠ Suspicious activity detected – entering safe mode'}
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default RobotLab
