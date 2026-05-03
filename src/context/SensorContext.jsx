import { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react'
import SensorAggregator from '../utils/sensorAggregator'
import { initKeyboardTracker } from '../utils/keyboardTracker'
import { startPeriodicRefresh } from '../services/newsEngine'
import { updateApiState } from '../utils/apiBridge'
// Diagnostics
import { startMonitoring, stopMonitoring, recordWorkerMessage, recordInferenceStart, recordInferenceEnd, updateWorkerStatus, logEvent } from '../utils/diagnostics'

const SensorContext = createContext(null)

const FACE_WORKER_URL = new URL('../workers/faceWorker.js', import.meta.url)
const VOICE_WORKER_URL = new URL('../workers/voiceWorker.js', import.meta.url)
const FUSION_WORKER_URL = new URL('../workers/fusionWorker.js', import.meta.url)

export function SensorProvider({ children }) {
  // Sensor state
  const [sensorActive, setSensorActive] = useState(false)
  const [sensorError, setSensorError] = useState(null)
  const [faceData, setFaceData] = useState(null)
  const [voiceData, setVoiceData] = useState(null)
  const [keyboardData, setKeyboardData] = useState(null)
  const [bufferFill, setBufferFill] = useState(0)

  // Fusion state
  const [fusionActive, setFusionActive] = useState(false)
  const [fusionResult, setFusionResult] = useState(null)
  const [fusionError, setFusionError] = useState(null)

  // Simulation state
  const [simulationActive, setSimulationActive] = useState(false)
  const [simulationInfo, setSimulationInfo] = useState(null) // { name, currentFrame, totalFrames }

  // Refs
  const aggregatorRef = useRef(new SensorAggregator(50))
  const faceWorkerRef = useRef(null)
  const voiceWorkerRef = useRef(null)
  const fusionWorkerRef = useRef(null)
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const audioContextRef = useRef(null)
  const processorRef = useRef(null)
  const cleanupKeyboardRef = useRef(null)
  const fusionLoopId = useRef(null)
  const simulationPlaybackId = useRef(null)

  // Diagnostics & bridge
  useEffect(() => {
    startMonitoring()
    logEvent('info', 'SensorContext', 'mounted')
    return () => {
      stopMonitoring()
      stopSimulation()
    }
  }, [])

  const pushDevState = useCallback(() => {
    if (!import.meta.env.DEV) return
    updateApiState('sensors', {
      faceData, voiceData, keyboardData, bufferFill,
      sensorActive: sensorActive || simulationActive
    })
    if (fusionResult) {
      const top = Object.entries(fusionResult.intentProbabilities).reduce((a,b)=>a[1]>b[1]?a:b)[0]
      updateApiState('intent', {
        intentProbabilities: fusionResult.intentProbabilities,
        topIntent: top,
        confidence: fusionResult.confidence,
        deceptionProbability: fusionResult.deceptionProbability
      })
    }
    updateApiState('status', {
      sensorsActive: sensorActive,
      fusionReady: fusionActive,
      usingSimulation: simulationActive,
      newsCacheSize: '~0.5 MB' // placeholder
    })
  }, [faceData, voiceData, keyboardData, bufferFill, sensorActive, simulationActive, fusionResult, fusionActive])

  // Broadcast state every 200ms in dev mode
  useEffect(() => {
    if (!import.meta.env.DEV) return
    let ra = null
    const tick = () => {
      pushDevState()
      ra = requestAnimationFrame(tick)
    }
    ra = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(ra)
  }, [pushDevState])

  /* ───────────── REAL SENSORS ───────────── */
  const startSensors = async () => {
    setSensorError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: { sampleRate: 16000, channelCount: 1 }
      })
      streamRef.current = stream
      const video = document.createElement('video')
      video.srcObject = stream
      video.playsInline = true
      await video.play()
      videoRef.current = video

      // Face worker
      const faceWorker = new Worker(FACE_WORKER_URL, { type: 'module' })
      faceWorkerRef.current = faceWorker
      faceWorker.onmessage = (e) => {
        const { type, gaze_x, gaze_y, au, timestamp } = e.data
        if (type === 'result') {
          setFaceData({ gaze_x, gaze_y, au })
          aggregatorRef.current.push({ timestamp, face: { gaze_x, gaze_y, au } })
          setBufferFill(aggregatorRef.current.getFillLevel())
          recordWorkerMessage('face')
          updateWorkerStatus('face', 'connected')
        } else if (type === 'error') {
          console.error('[FaceWorker]', e.data.message)
          updateWorkerStatus('face', 'error')
        }
      }
      faceWorker.postMessage({ type: 'init' })

      // Voice worker
      const voiceWorker = new Worker(VOICE_WORKER_URL, { type: 'module' })
      voiceWorkerRef.current = voiceWorker
      voiceWorker.onmessage = (e) => {
        const { type, mfcc, pitch, loudness, jitter, shimmer, timestamp } = e.data
        if (type === 'result') {
          setVoiceData({ mfcc, pitch, loudness, jitter, shimmer })
          const current = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
          if (current && !current.voice) current.voice = { mfcc, pitch, loudness, jitter, shimmer }
          else aggregatorRef.current.push({ timestamp, voice: { mfcc, pitch, loudness, jitter, shimmer } })
          setBufferFill(aggregatorRef.current.getFillLevel())
          recordWorkerMessage('voice')
          updateWorkerStatus('voice', 'connected')
        } else if (type === 'error') {
          console.error('[VoiceWorker]', e.data.message)
          updateWorkerStatus('voice', 'error')
        }
      }

      const audioCtx = new AudioContext({ sampleRate: 16000 })
      audioContextRef.current = audioCtx
      const source = audioCtx.createMediaStreamSource(stream)
      const processor = audioCtx.createScriptProcessor(4096, 1, 1)
      processor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer.getChannelData(0)
        const bufferCopy = new Float32Array(inputBuffer)
        voiceWorker.postMessage({ type: 'audio', buffer: bufferCopy, sampleRate: 16000, timestamp: performance.now() }, [bufferCopy.buffer])
      }
      source.connect(processor)
      processor.connect(audioCtx.destination)
      processorRef.current = processor

      // Keyboard
      const cleanupKeyboard = initKeyboardTracker((kbData) => {
        setKeyboardData(kbData)
        const current = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
        if (current && !current.keyboard) current.keyboard = kbData
        else aggregatorRef.current.push({ timestamp: performance.now(), keyboard: kbData })
        setBufferFill(aggregatorRef.current.getFillLevel())
      })
      cleanupKeyboardRef.current = cleanupKeyboard

      // Fusion worker
      const fusionWorker = new Worker(FUSION_WORKER_URL, { type: 'module' })
      fusionWorkerRef.current = fusionWorker
      fusionWorker.onmessage = (e) => {
        const { type, intentProbabilities, embedding, confidence, deceptionProbability, timestamp } = e.data
        if (type === 'result') {
          setFusionResult({ intentProbabilities, embedding, confidence, deceptionProbability, timestamp })
          setFusionActive(true)
          recordWorkerMessage('fusion')
          updateWorkerStatus('fusion', 'connected')
          recordInferenceEnd()
        } else if (type === 'error') {
          console.error('[FusionWorker]', e.data.message)
          setFusionError(e.data.message)
          updateWorkerStatus('fusion', 'error')
        } else if (type === 'ready') {
          console.log('[FusionWorker] Model ready – inference enabled')
          setFusionActive(true)
          updateWorkerStatus('fusion', 'connected')
          logEvent('info', 'Fusion', `Loaded in ${e.data.mode || 'ONNX'} mode`)
        }
      }
      fusionWorker.postMessage({ type: 'init' })

      const runFusion = () => {
        if (aggregatorRef.current.getFillLevel() >= 50) {
          recordInferenceStart()
          const tensor = aggregatorRef.current.getTensorInput()
          fusionWorker.postMessage({ type: 'tensor', data: tensor })
        }
        fusionLoopId.current = requestAnimationFrame(runFusion)
      }
      setTimeout(() => { runFusion() }, 500)

      setSensorActive(true)
      console.log('[SensorContext] All sensors started')
    } catch (err) {
      console.error('[SensorContext] startup error:', err)
      setSensorError(`Could not start sensors: ${err.message}`)
    }
  }

  /* ───────────── STOP ───────────── */
  const stopSensors = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    if (processorRef.current) { processorRef.current.disconnect(); processorRef.current = null }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    if (faceWorkerRef.current) {
      faceWorkerRef.current.postMessage({ type: 'close' })
      faceWorkerRef.current.terminate()
      faceWorkerRef.current = null
    }
    if (voiceWorkerRef.current) {
      voiceWorkerRef.current.postMessage({ type: 'close' })
      voiceWorkerRef.current.terminate()
      voiceWorkerRef.current = null
    }
    if (fusionWorkerRef.current) {
      fusionWorkerRef.current.postMessage({ type: 'close' })
      fusionWorkerRef.current.terminate()
      fusionWorkerRef.current = null
    }
    if (fusionLoopId.current) {
      cancelAnimationFrame(fusionLoopId.current)
      fusionLoopId.current = null
    }
    if (cleanupKeyboardRef.current) {
      cleanupKeyboardRef.current()
      cleanupKeyboardRef.current = null
    }
    setSensorActive(false)
    setFaceData(null)
    setVoiceData(null)
    setKeyboardData(null)
    aggregatorRef.current.reset()
    setBufferFill(0)
    console.log('[SensorContext] Sensors stopped')
  }, [])

  /* ───────────── SIMULATION ───────────── */
  const injectSimulationFrame = useCallback((frame) => {
    const ts = performance.now()
    if (frame.face) {
      setFaceData(frame.face)
      aggregatorRef.current.push({ timestamp: ts, face: frame.face })
    }
    if (frame.voice) {
      setVoiceData(frame.voice)
      const last = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
      if (last && !last.voice) last.voice = frame.voice
      else aggregatorRef.current.push({ timestamp: ts, voice: frame.voice })
    }
    if (frame.keyboard) {
      setKeyboardData(frame.keyboard)
      const last = aggregatorRef.current.buffer[aggregatorRef.current.buffer.length - 1]
      if (last && !last.keyboard) last.keyboard = frame.keyboard
      else aggregatorRef.current.push({ timestamp: ts, keyboard: frame.keyboard })
    }
    setBufferFill(aggregatorRef.current.getFillLevel())
  }, [])

  const startSimulation = (scenario) => {
    stopSensors()
    setSimulationActive(true)
    setSimulationInfo({ name: scenario.name, currentFrame: 0, totalFrames: scenario.frames.length })

    let idx = 0
    const fps = 20
    const interval = 1000 / fps

    const play = () => {
      if (!simulationActive) return
      if (idx >= scenario.frames.length) {
        setSimulationActive(false)
        setSimulationInfo(null)
        return
      }
      injectSimulationFrame(scenario.frames[idx])
      idx++
      setSimulationInfo(prev => prev ? { ...prev, currentFrame: idx } : null)
      simulationPlaybackId.current = setTimeout(() => requestAnimationFrame(play), interval)
    }
    play()
  }

  const stopSimulation = () => {
    setSimulationActive(false)
    setSimulationInfo(null)
    if (simulationPlaybackId.current) {
      clearTimeout(simulationPlaybackId.current)
      simulationPlaybackId.current = null
    }
  }

  // News refresh
  useEffect(() => {
    startPeriodicRefresh(5 * 60 * 1000)
    return () => {}
  }, [])

  const value = {
    sensorActive,
    sensorError,
    faceData,
    voiceData,
    keyboardData,
    bufferFill,
    startSensors,
    stopSensors,
    aggregator: aggregatorRef.current,
    getLatestVector: () => aggregatorRef.current.getLatestVector(),
    getTensorInput: () => aggregatorRef.current.getTensorInput(),
    fusionActive,
    fusionResult,
    fusionError,
    simulationActive,
    simulationInfo,
    startSimulation,
    stopSimulation
  }

  return (
    <SensorContext.Provider value={value}>
      {children}
    </SensorContext.Provider>
  )
}

// Export hook for convenient consumption
// eslint-disable-next-line react-refresh/only-export-components
export function useSensor() {
  const context = useContext(SensorContext)
  if (!context) throw new Error('useSensor must be used within a SensorProvider')
  return context
}
