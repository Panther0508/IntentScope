import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="container">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title text-gold">
            IntentScope – Read the Unspoken
          </h1>
          <p className="hero-subtitle text-muted">
            Real-time intention analysis · Browser-based · No data leaves your device
          </p>
          <div className="hero-actions">
            <Link to="/dashboard" className="btn btn-gold">
              Launch Dashboard
            </Link>
            <Link to="/robot" className="btn btn-outline">
              Try the Robot Lab
            </Link>
          </div>
        </div>

        {/* Mindscape placeholder */}
        <div className="mindscape-placeholder">
          <div className="dashed-box">
            <p className="text-gold uppercase">3-D Mindscape - Coming Soon</p>
            <p className="text-muted">Particle Cloud Visualization</p>
          </div>
        </div>
      </section>

      {/* Feature grid */}
      <section className="features">
        <div className="features-grid">
          <div className="card feature-card">
            <h3>Face & Gaze Tracking</h3>
            <p className="text-muted">
              High-precision facial landmark detection and gaze vector extraction using MediaPipe. Track micro-expressions in real-time.
            </p>
          </div>
          <div className="card feature-card">
            <h3>Voice Stress Analysis</h3>
            <p className="text-muted">
              Extract audio features with Meyda and detect emotional stress patterns in speech. All processing happens locally.
            </p>
          </div>
          <div className="card feature-card">
            <h3>Local AI Fusion</h3>
            <p className="text-muted">
              A custom ONNX neural network fuses face, voice, and behavioral signals into a unified intent prediction model.
            </p>
          </div>
          <div className="card feature-card">
            <h3>Explainable Predictions</h3>
            <p className="text-muted">
              The AI narrator explains its reasoning in natural language, giving you transparent insight into detected intentions.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
