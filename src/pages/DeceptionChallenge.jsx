import { useState, useEffect, useRef } from 'react'
import { useSensor } from '../context/SensorContext'

const CHALLENGE_QUESTIONS = [
  "Have you ever lied to a close friend?",
  "Are you currently hiding something from someone?",
  "Did you take the last cookie from the jar?",
  "Do you sometimes pretend to be more productive than you are?",
  "Have you ever exaggerated your skills on a resume?"
]

function DeceptionChallenge() {
  const { sensorActive, fusionActive, fusionResult, startSensors } = useSensor()
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [phase, setPhase] = useState('idle') // idle, question, answering, result
  const [answer, setAnswer] = useState(null)
  const [verdict, setVerdict] = useState(null)
  const [scores, setScores] = useState([])
  const timerRef = useRef(null)

  const currentQuestion = CHALLENGE_QUESTIONS[currentQuestionIdx]

  // Auto-start sensors if not active when page opens
  useEffect(() => {
    if (!sensorActive) {
      startSensors()
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startQuestion = () => {
    setPhase('question')
    setAnswer(null)
    setVerdict(null)
    // Show question for 5 seconds, then prompt for answer
    timerRef.current = setTimeout(() => {
      setPhase('answering')
    }, 5000)
  }

  const handleAnswer = (userSaidTrue) => {
    if (phase !== 'answering') return
    setAnswer(userSaidTrue)
    setPhase('result')

    // Evaluate deception based on fusion model (ground truth unknown)
    if (fusionActive && fusionResult) {
      const deceptionProb = fusionResult.deceptionProbability
      // Verdict: if user said truth but model thinks lying → potential deception
      // Simplified: verdict based purely on probability (we don't know actual truth)
      const verdictText = deceptionProb > 0.6
        ? 'Elevated deception indicators detected.'
        : deceptionProb > 0.3
          ? 'Slight unease detected.'
          : 'Responses appear truthful.'
      setVerdict(verdictText)
      setScores(prev => [...prev, Math.round(deceptionProb * 100)])
    }

    // Move to next question after delay
    timerRef.current = setTimeout(() => {
      const next = currentQuestionIdx + 1
      if (next < CHALLENGE_QUESTIONS.length) {
        setCurrentQuestionIdx(next)
        setPhase('idle')
      } else {
        setPhase('complete')
      }
    }, 5000)
  }

  const restart = () => {
    setCurrentQuestionIdx(0)
    setPhase('idle')
    setScores([])
    setAnswer(null)
    setVerdict(null)
  }

  return (
    <div className="container deception-page">
      <h2>Deception Challenge</h2>

      {phase === 'complete' ? (
        <div className="card summary-card">
          <h3>Challenge Complete</h3>
          <p className="text-muted">Your average deception indicator: {scores.length ? Math.round(scores.reduce((a,b)=>a+b)/scores.length) : 0}%</p>
          <div className="score-history">
            {scores.map((s, i) => (
              <div key={i} className="score-item">
                <span>Q{i+1}:</span>
                <span className="text-gold">{s}%</span>
              </div>
            ))}
          </div>
          <button className="btn btn-gold" onClick={restart}>Try Again</button>
        </div>
      ) : (
        <>
          <div className="challenge-layout">
            {/* Question */}
            <div className="card question-card">
              <h3 className="text-mono">Question {currentQuestionIdx + 1}/{CHALLENGE_QUESTIONS.length}</h3>
              <p className="question-text">
                {phase === 'question' ? currentQuestion : (answer !== null ? (answer ? 'You answered: TRUE' : 'You answered: FALSE') : 'Get ready...')}
              </p>
              {phase === 'question' && <div className="countdown">Answer in 5 seconds...</div>}
            </div>

            {/* Webcam */}
            <div className="card camera-card">
              <h3 className="text-mono">Live Feed</h3>
              <div className="webcam-container">
                <video
                  id="deception-webcam"
                  autoPlay
                  muted
                  playsInline
                  style={{ width: '100%', height: 'auto', transform: 'scaleX(-1)' }}
                />
              </div>
            </div>

            {/* Fake controls */}
            <div className="controls">
              {phase === 'idle' && (
                <button className="btn btn-gold" onClick={startQuestion}>Start Question</button>
              )}
              {phase === 'answering' && (
                <>
                  <button className="btn btn-gold" onClick={() => handleAnswer(true)}>TRUE</button>
                  <button className="btn btn-outline" onClick={() => handleAnswer(false)}>FALSE</button>
                </>
              )}
              {phase === 'result' && (
                <div className="verdict-box">
                  <p className="verdict-text">{verdict}</p>
                  {scores.length > 0 && (
                    <p className="deception-score">Last score: {scores[scores.length-1]}%</p>
                  )}
                </div>
              )}
            </div>

            {/* Scoreboard */}
            <div className="card scoreboard">
              <h3 className="text-mono">Live Metrics</h3>
              {fusionActive ? (
                <div className="score-item">
                  <span>Deception Probability:</span>
                  <span className="text-gold">{fusionResult?.deceptionProbability ? Math.round(fusionResult.deceptionProbability * 100) : 0}%</span>
                </div>
              ) : (
                <p className="text-muted">Fusion model loading...</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default DeceptionChallenge
