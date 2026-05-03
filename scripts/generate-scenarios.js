#!/usr/bin/env node
// generate-scenarios.js – creates synthetic sensor scenario files

const fs = require('fs')
const path = require('path')

function randomRange(min, max) { return Math.random() * (max - min) + min }

function gaussian(mean, stdev) {
  const u = 1 - Math.random()
  const v = Math.random()
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v)
  return z * stdev + mean
}

function clamp(v, min, max) { return Math.min(Math.max(v, min), max) }

function createScenario(name, duration, config) {
  const fps = 20
  const totalFrames = Math.floor(duration * fps)
  const timestamps = []
  const frames = []

  for (let i = 0; i < totalFrames; i++) {
    const t = i / fps
    timestamps.push(parseFloat(t.toFixed(2)))

    // Face: gaze wandering + occasional AU spikes
    const phase = t * 0.5
    const gaze_x = Math.sin(phase) * 0.3 + Math.sin(t * 2.3) * 0.1
    const gaze_y = Math.cos(phase * 0.7) * 0.2

    const au = Array(6).fill(0).map((_, j) => {
      const base = Math.sin(t * (0.5 + j * 0.2)) * 0.1
      const spike = Math.random() < 0.02 ? Math.random() * 1.5 : 0
      return clamp(base + spike, 0, 1.5)
    })

    // Voice: MFCC-ish, pitch, loudness + noise
    const mfcc = Array(13).fill(0).map(() => clamp(gaussian(0, 0.5), -2, 2))
    const pitch = clamp(0.3 + Math.sin(t * 1.5) * 0.2 + Math.random() * 0.1, 0, 1)
    const loudness = clamp(0.4 + (config.energy || 0.3) + Math.sin(t * 0.8) * 0.2, 0, 1)
    const jitter = clamp(Math.random() * 0.02, 0, 0.05)
    const shimmer = clamp(Math.random() * 0.03, 0, 0.06)

    // Keyboard: mostly null, occasional typing bursts
    let keyboard = null
    if (config.typing && Math.random() < config.typingRate) {
      keyboard = {
        interKeyInterval: randomRange(80, 200),
        holdDuration: randomRange(40, 120),
        variance: randomRange(10, 50),
        typingSpeed: randomRange(40, 80)
      }
    }

    frames.push({
      face: { gaze_x, gaze_y, au },
      voice: { mfcc, pitch, loudness, jitter, shimmer },
      keyboard
    })
  }

  return {
    name,
    duration,
    timestamps,
    frames,
    description: config.description || ''
  }
}

const scenarios = {
  exploring: createScenario('exploring', 12, {
    description: 'Curious browsing – gaze moves around, low stress, occasional typing',
    energy: 0.2,
    typing: true,
    typingRate: 0.15
  }),
  buy_intent: createScenario('buy_intent', 10, {
    description: 'High excitement, focused gaze, regular typing patterns',
    energy: 0.6,
    typing: true,
    typingRate: 0.25
  }),
  deceptive_response: createScenario('deceptive_response', 8, {
    description: 'Hesitation spikes, voice jitter high, gaze aversion, irregular typing',
    energy: 0.4,
    typing: true,
    typingRate: 0.08
  })
}

const outDir = path.join(__dirname, 'public', 'scenarios')
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true })

for (const [name, data] of Object.entries(scenarios)) {
  const filePath = path.join(outDir, `${name}.json`)
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2))
  console.log(`Generated: ${name}.json (${data.frames.length} frames, ${(data.duration).toFixed(1)}s)`)
}

console.log('All scenarios written to', outDir)
