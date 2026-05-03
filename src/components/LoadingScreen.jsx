import { useEffect, useState } from 'react'

function LoadingScreen({ onComplete }) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setTimeout(() => onComplete?.(), 300)
          return 100
        }
        return prev + Math.random() * 15 + 5
      })
    }, 200)

    return () => clearInterval(interval)
  }, [onComplete])

  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loading-logo">
          <span className="loading-dot"></span>
          <span className="loading-text">IntentScope</span>
        </div>
        <p className="loading-subtitle">Initializing neural engine...</p>
        <div className="progress-container">
          <div className="progress-bar" style={{ width: `${Math.min(progress, 100)}%` }}></div>
        </div>
        <p className="progress-text">{Math.round(Math.min(progress, 100))}%</p>
      </div>
    </div>
  )
}

export default LoadingScreen
