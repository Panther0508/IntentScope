import { Outlet, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import useStarfield from '../hooks/useStarfield'
import './Layout.css'

function Layout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const canvasRef = useStarfield()

  return (
    <div className="layout">
      {/* Starfield background */}
      <canvas ref={canvasRef} className="starfield" />

      {/* Header */}
      <header className="header glass">
        <div className="header-inner container">
          <div className="logo">
            <span className="logo-dot"></span>
            <span className="logo-text">IntentScope</span>
            <span className="live-indicator"></span>
          </div>

          {/* Desktop navigation */}
          <nav className="nav">
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Dashboard
            </NavLink>
            <NavLink to="/analysis" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Analysis
            </NavLink>
            <NavLink to="/robot" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Robot Lab
            </NavLink>
            <NavLink to="/narrator" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Narrator
            </NavLink>
            <NavLink to="/deception" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Deception
            </NavLink>
          </nav>

          {/* Mobile menu button */}
          <button className="menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? '✕' : '☰'}
          </button>
        </div>

        {/* Mobile nav dropdown */}
        {menuOpen && (
          <nav className="mobile-nav">
            <NavLink to="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</NavLink>
            <NavLink to="/analysis" onClick={() => setMenuOpen(false)}>Analysis</NavLink>
            <NavLink to="/robot" onClick={() => setMenuOpen(false)}>Robot Lab</NavLink>
            <NavLink to="/narrator" onClick={() => setMenuOpen(false)}>Narrator</NavLink>
            <NavLink to="/deception" onClick={() => setMenuOpen(false)}>Deception</NavLink>
          </nav>
        )}
      </header>

      {/* Gold separator line */}
      <div className="gold-line"></div>

      {/* Main content */}
      <main className="main">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>Powered by open-source AI · All processing on-device · Built by Panther0508</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
