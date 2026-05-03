/**
 * Simulator – Replay sensor scenarios & record live sessions
 */

// Scenario file format:
// {
//   name: "exploring",
//   duration: 15.2,
//   timestamps: [0.00, 0.05, 0.10, ...],
//   frames: [
//     { face: {...}, voice: {...}, keyboard: {...} },
//     ...
//   ]
// }

class Simulator {
  constructor(aggregator, onFrame) {
    this.aggregator = aggregator
    this.onFrame = onFrame
    this.scenario = null
    this.isPlaying = false
    this.isPaused = false
    this.currentIndex = 0
    this.speed = 1.0
    this.startTime = 0
    this.pausedTime = 0
    this.playbackId = null
    this.recordedFrames = []
    this.isRecording = false
  }

  load(scenario) {
    this.stop()
    this.scenario = scenario
    this.currentIndex = 0
    this.pausedTime = 0
    console.log(`[Simulator] Loaded scenario: ${scenario.name} (${scenario.duration.toFixed(1)}s, ${scenario.frames.length} frames)`)
  }

  play() {
    if (!this.scenario) return
    this.isPlaying = true
    this.isPaused = false
    this.startTime = performance.now() - (this.pausedTime * 1000)

    const tick = () => {
      if (!this.isPlaying || this.isPaused) return

      const elapsed = (performance.now() - this.startTime) / 1000 * this.speed
      const targetIndex = Math.floor(elapsed / 0.05) // 20 Hz fixed timestep

      if (targetIndex >= this.scenario.frames.length) {
        this.stop()
        return
      }

      if (targetIndex > this.currentIndex) {
        this.currentIndex = targetIndex
        const frame = this.scenario.frames[this.currentIndex]
        const timestamp = performance.now()

        // Inject into aggregator
        this.aggregator.push({
          timestamp,
          face: frame.face,
          voice: frame.voice,
          keyboard: frame.keyboard
        })

        // Callback for UI updates
        if (this.onFrame) this.onFrame(frame, this.currentIndex, this.scenario.frames.length)
      }

      this.playbackId = requestAnimationFrame(tick)
    }

    tick()
  }

  pause() {
    this.isPaused = true
    this.pausedTime = (performance.now() - this.startTime) / 1000 * this.speed
    cancelAnimationFrame(this.playbackId)
  }

  resume() {
    if (this.isPaused) {
      this.isPaused = false
      this.play()
    }
  }

  stop() {
    this.isPlaying = false
    this.isPaused = false
    cancelAnimationFrame(this.playbackId)
    this.currentIndex = 0
    this.pausedTime = 0
    if (this.onFrame) this.onFrame(null, 0, this.scenario?.frames.length || 0)
  }

  seek(seconds) {
    if (!this.scenario) return
    const index = Math.min(Math.floor(seconds / 0.05), this.scenario.frames.length - 1)
    this.currentIndex = index
    this.pausedTime = seconds * 1000
    if (this.isPlaying) {
      this.startTime = performance.now() - this.pausedTime
    }
    // Inject this frame immediately
    const frame = this.scenario.frames[index]
    this.aggregator.push({
      timestamp: performance.now(),
      face: frame.face,
      voice: frame.voice,
      keyboard: frame.keyboard
    })
    if (this.onFrame) this.onFrame(frame, index, this.scenario.frames.length)
  }

  setSpeed(multiplier) {
    this.speed = multiplier
  }

  // Recording: capture live sensor data into recordedFrames
  startRecording() {
    this.recordedFrames = []
    this.isRecording = true
  }

  recordFrame(faceData, voiceData, keyboardData) {
    if (!this.isRecording) return
    this.recordedFrames.push({
      timestamp: performance.now(),
      face: faceData,
      voice: voiceData,
      keyboard: keyboardData
    })
  }

  stopRecording() {
    this.isRecording = false
    return this.recordedFrames
  }

  downloadRecording(name = 'session') {
    const frames = this.stopRecording()
    if (frames.length === 0) return

    const scenario = {
      name,
      duration: frames.length * 0.05,
      timestamps: frames.map((_, i) => i * 0.05),
      frames
    }

    const blob = new Blob([JSON.stringify(scenario, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${name}-${new Date().toISOString().slice(0,10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }
}

// Pre-loaded scenarios (will be fetched as JSON from public/scenarios/)
export async function loadScenarioFromFile(name) {
  const resp = await fetch(`/scenarios/${name}.json`)
  if (!resp.ok) throw new Error(`Scenario ${name} not found`)
  return await resp.json()
}

export function createSimulator(aggregator, onFrame) {
  return new Simulator(aggregator, onFrame)
}
