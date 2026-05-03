import { describe, it, expect, beforeEach, vi } from 'vitest'
import { initKeyboardTracker } from '../utils/keyboardTracker'

describe('KeyboardTracker', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should call callback on keyup after keydown', () => {
    const callback = vi.fn()
    const cleanup = initKeyboardTracker(callback)

    const down = new KeyboardEvent('keydown', { key: 'a', timeStamp: 1000 })
    window.dispatchEvent(down)

    const up = new KeyboardEvent('keyup', { key: 'a', timeStamp: 1100 })
    window.dispatchEvent(up)

    expect(callback).toHaveBeenCalledTimes(1)
    const result = callback.mock.calls[0][0]
    expect(result).toHaveProperty('interKeyInterval')
    expect(result).toHaveProperty('holdDuration')
    expect(result).toHaveProperty('variance')
  })

  it('should cleanup and stop callbacks after cleanup', () => {
    const callback = vi.fn()
    const cleanup = initKeyboardTracker(callback)

    // Simulate some events
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', timeStamp: 1000 }))
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'a', timeStamp: 1100 }))
    expect(callback).toHaveBeenCalled()

    cleanup()
    // After cleanup, no more callbacks
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'b', timeStamp: 2000 }))
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'b', timeStamp: 2100 }))
    expect(callback).toHaveBeenCalledTimes(1) // still only 1
  })

  it('should calculate interKeyInterval between successive keys', () => {
    const callback = vi.fn()
    initKeyboardTracker(callback)

    // First key pair
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', timeStamp: 1000 }))
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'a', timeStamp: 1100 }))

    // Second key after 150ms (keydown at 1150)
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'b', timeStamp: 1150 }))
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'b', timeStamp: 1250 }))

    expect(callback).toHaveBeenCalledTimes(2)
    const secondCall = callback.mock.calls[1][0]
    // interKeyInterval should be 150ms (difference between first and second keydown)
    expect(secondCall.interKeyInterval).toBe(150)
  })
})
