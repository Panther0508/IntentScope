import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import LoadingScreen from './components/LoadingScreen.jsx'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Analysis from './pages/Analysis.jsx'
import RobotLab from './pages/RobotLab.jsx'
import AINarrator from './pages/AINarrator.jsx'
import DeceptionChallenge from './pages/DeceptionChallenge.jsx'
import About from './pages/About.jsx'
import Settings from './pages/Settings.jsx'
import Diagnostics from './pages/Diagnostics.jsx'
import Playground from './pages/Playground.jsx'
import Tutorial from './pages/Tutorial.jsx'
import ApiPlayground from './pages/ApiPlayground.jsx'
import ContributingPage from './pages/ContributingPage.jsx'
import './db.js'

function App() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2200)
    return () => clearTimeout(timer)
  }, [])

  if (loading) return <LoadingScreen onComplete={() => setLoading(false)} />

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
        <Route path="diagnostics" element={<Diagnostics />} />
        <Route path="playground" element={<Playground />} />
        <Route path="tutorial" element={<Tutorial />} />
        <Route path="api-playground" element={<ApiPlayground />} />
        <Route path="contribute" element={<ContributingPage />} />
      </Route>
    </Routes>
  )
}

export default App
