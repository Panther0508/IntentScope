function RobotLab() {
  return (
    <div className="robot-lab">
      <aside className="sidebar glass">
        <h3>Controls</h3>
        <ul className="hints">
          <li>Look at an object + raise eyebrows to grab</li>
          <li>Tilt head left/right to rotate wrist</li>
          <li>Blink rapidly toggles gripper</li>
        </ul>
      </aside>

      <main className="robot-main">
        <h2>Robotic Arm – Gaze Control</h2>
        <div id="robot-canvas" className="robot-viewport">
          <div className="loading-message">
            <span className="text-gold">Robot arm loading...</span>
            <p className="text-muted">Three.js scene will appear here</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default RobotLab
