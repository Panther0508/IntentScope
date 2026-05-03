import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../pages/Home'

describe('Home Page', () => {
  it('renders hero title', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByText(/Real-time intention analysis/i)).toBeInTheDocument()
  })

  it('has call-to-action button', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    expect(screen.getByRole('link', { name: /try the robot lab/i })).toBeInTheDocument()
  })
})
