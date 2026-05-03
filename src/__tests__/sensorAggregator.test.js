import { describe, it, expect, beforeEach } from 'vitest'
import SensorAggregator from '../utils/sensorAggregator'

describe('SensorAggregator', () => {
  let aggregator

  beforeEach(() => {
    aggregator = new SensorAggregator(50) // window size 50
  })

  it('should initialize with empty buffer', () => {
    expect(aggregator.buffer.length).toBe(0)
    expect(aggregator.getFillLevel()).toBe(0)
  })

  it('should push face data and increment fill level', () => {
    const timestamp = 1000
    const faceData = { gaze_x: 0.5, gaze_y: 0.5, au: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6] }

     aggregator.push({ timestamp, face: faceData })

     // Buffer should have one entry with face data
     expect(aggregator.buffer.length).toBe(1)
     expect(aggregator.buffer[0]).toMatchObject({ timestamp, face: faceData })
     expect(aggregator.getFillLevel()).toBe(1)
  })

  it('should push voice data as separate entry', () => {
    aggregator.push({ timestamp: 1000, face: { gaze_x: 0.5, gaze_y: 0.5, au: [1,2,3,4,5,6] } })
    aggregator.push({ timestamp: 1001, voice: { mfcc: [0.1,0.2], pitch: 0.3, loudness: 0.4, jitter: 0.5, shimmer: 0.6 } })

    // Two separate entries unless merged externally
    expect(aggregator.buffer.length).toBe(2)
    expect(aggregator.buffer[0].face).not.toBeNull()
    expect(aggregator.buffer[1].voice).not.toBeNull()
  })

  it('should maintain sliding window of 50 timesteps', () => {
    // Push 60 entries with simple incremental timestamps
    for (let i = 0; i < 60; i++) {
      aggregator.push({
        timestamp: i,
        face: { gaze_x: i/100, gaze_y: i/100, au: [0,0,0,0,0,0] },
        voice: { mfcc: [0], pitch: 0, loudness: 0, jitter: 0, shimmer: 0 }
      })
    }

    expect(aggregator.buffer.length).toBe(50)
    // After shifting, the oldest entry should be at index 0 (timestamp 10)
    expect(aggregator.buffer[0].timestamp).toBe(10) // first 10 shifted out
    expect(aggregator.buffer[49].timestamp).toBe(59) // newest
  })

  it('should get a 28-D feature vector for the latest timestep', () => {
    aggregator.push({
      timestamp: 1000,
      face: { gaze_x: 0.5, gaze_y: 0.5, au: [0.1,0.2,0.3,0.4,0.5,0.6] },
      voice: {
        mfcc: Array(13).fill(0.1),
        pitch: 0.2,
        loudness: 0.3,
        jitter: 0.4,
        shimmer: 0.5
      },
      keyboard: {
        interKeyInterval: 100,
        holdDuration: 50,
        variance: 10,
        typingSpeed: 60
      }
    })

    const vector = aggregator.getLatestVector()
    expect(vector.length).toBe(29)
    expect(vector).toBeInstanceOf(Float32Array)
  })

  it('should get a tensor input with padding when buffer not full', () => {
    aggregator.push({
      timestamp: 1000,
      face: { gaze_x: 0, gaze_y: 0, au: [0,0,0,0,0,0] }
    })
    const tensor = aggregator.getTensorInput()
    expect(tensor.length).toBe(50 * 29) // always returns full window
  })

  it('should return a full-size tensor when buffer is full', () => {
    for (let i = 0; i < 50; i++) {
      aggregator.push({
        timestamp: 1000 + i,
        face: { gaze_x: 0.5, gaze_y: 0.5, au: [0.1,0.2,0.3,0.4,0.5,0.6] },
        voice: { mfcc: Array(13).fill(0.1), pitch: 0.2, loudness: 0.3, jitter: 0.4, shimmer: 0.5 },
        keyboard: { interKeyInterval: 100, holdDuration: 50, variance: 10, typingSpeed: 60 }
      })
    }
    const tensor = aggregator.getTensorInput()
    expect(tensor.length).toBe(50 * 29)
  })
})
