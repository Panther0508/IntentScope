import { useEffect, useRef } from 'react'

// Simple starfield effect using canvas 2D
export default function useStarfield() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let animationFrameId
    let stars = []

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      initStars()
    }

    const initStars = () => {
      stars = []
      const count = Math.floor((canvas.width * canvas.height) / 8000)
      for (let i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          size: Math.random() * 2,
          speed: Math.random() * 0.3 + 0.1,
          opacity: Math.random() * 0.5 + 0.3,
        })
      }
    }

    const draw = () => {
      ctx.fillStyle = 'rgba(5, 5, 5, 0.1)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      stars.forEach(star => {
        ctx.beginPath()
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(212, 175, 55, ${star.opacity})`
        ctx.fill()

        star.y -= star.speed
        if (star.y < 0) {
          star.y = canvas.height
          star.x = Math.random() * canvas.width
        }
      })

      animationFrameId = requestAnimationFrame(draw)
    }

    window.addEventListener('resize', resize)
    resize()
    draw()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return canvasRef
}
