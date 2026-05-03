import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import LoadingScreen from './components/LoadingScreen'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import RobotLab from './pages/RobotLab'
import AINarrator from './pages/AINarrator'
import DeceptionChallenge from './pages/DeceptionChallenge'
import About from './pages/About'
import Settings from './pages/Settings'
import './db' // Initialize IndexedDB

function App() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate initial loading time for models & assets
    const timer = setTimeout(() => {
      setLoading(false)
    }, 2200)

    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return <LoadingScreen onComplete={() => setLoading(false)} />
  }

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analysis" element={<Analysis />} />
        <Route path="robot" element={<RobotLab />} />
        <Route path="narrator" element={<AINarrator />} />
        <Route path="deception" element={<DeceptionChallenge />} />
        <Route path="about" element={<About />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
