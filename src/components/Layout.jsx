import { Outlet, Link, useLocation } from 'react-router-dom'
import DiagnosticsOverlay from './DiagnosticsOverlay'

function Layout() {
  const location = useLocation()

  return (
    <div className="layout">
      {/* Navigation */}
      <nav className="nav">
        <div className="nav-brand">
          <Link to="/">
            <span className="logo">⚡ IntentScope</span>
          </Link>
        </div>
        <ul className="nav-links">
          <li><Link to="/" className={location.pathname === '/' ? 'active' : ''}>Home</Link></li>
          <li><Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link></li>
          <li><Link to="/analysis" className={location.pathname === '/analysis' ? 'active' : ''}>Analysis</Link></li>
          <li><Link to="/playground" className={location.pathname === '/playground' ? 'active' : ''}>Playground</Link></li>
          <li><Link to="/robot" className={location.pathname === '/robot' ? 'active' : ''}>Robot Lab</Link></li>
          <li><Link to="/narrator" className={location.pathname === '/narrator' ? 'active' : ''}>Narrator</Link></li>
          <li><Link to="/deception" className={location.pathname === '/deception' ? 'active' : ''}>Deception</Link></li>
          <li><Link to="/tutorial" className={location.pathname === '/tutorial' ? 'active' : ''}>Tutorial</Link></li>
          <li><Link to="/api-playground" className={location.pathname === '/api-playground' ? 'active' : ''}>API</Link></li>
          <li><Link to="/diagnostics" className={location.pathname === '/diagnostics' ? 'active' : ''}>Diagnostics</Link></li>
          <li><Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>About</Link></li>
          <li><Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>Settings</Link></li>
        </ul>
      </nav>

      {/* Main content */}
      <main className="main">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          IntentScope v1.0.0 • Written by <a href="https://github.com/Panther0508" target="_blank" rel="noopener noreferrer">Panther0508</a>
          {' • '}
          <a href="https://github.com/Panther0508/IntentScope" target="_blank" rel="noopener noreferrer">GitHub</a>
        </p>
      </footer>

      {/* Diagnostics overlay – dev only */}
      {import.meta.env.DEV && <DiagnosticsOverlay />}
    </div>
  )
}

export default Layout
