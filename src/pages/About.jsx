function About() {
  return (
    <div className="container about-page">
      <h2>About IntentScope</h2>

      <div className="about-content">
        <section className="card">
          <h3>The Project</h3>
          <p className="text-muted">
            IntentScope is a cutting-edge, browser-based platform for real-time intention reading.
            Using only client-side processing, it captures facial expressions, voice stress, keyboard dynamics,
            and fuses them through a neural network to predict user intent. All data stays on your device.
          </p>
        </section>

        <section className="card">
          <h3>Technology Stack</h3>
          <ul className="tech-list text-mono">
            <li>MediaPipe Tasks Vision – Face landmarking & gaze estimation</li>
            <li>Meyda – Real-time audio feature extraction</li>
            <li>ONNX Runtime Web – Local neural network inference</li>
            <li>WebLLM (MLC) – On-device large language model</li>
            <li>Three.js – 3D robotic arm & particle visualization</li>
            <li>Dexie (IndexedDB) – Model caching & session storage</li>
          </ul>
        </section>

        <section className="card">
          <h3>Built By</h3>
          <p className="text-muted">
            Panther0508 – Independent AI researcher & full-stack engineer
          </p>
          <a
            href="https://github.com/Panther0508"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gold"
          >
            GitHub Profile →
          </a>
        </section>
      </div>
    </div>
  )
}

export default About
