import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Navbar } from '../Navbar'

describe('Navbar', () => {
  const renderNavbar = () => {
    return render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
  }

  it('renders the logo/brand name', () => {
    renderNavbar()
    expect(screen.getByText('TDD Demo')).toBeInTheDocument()
  })

  it('renders login and register links', () => {
    renderNavbar()
    
    const loginLink = screen.getByRole('link', { name: /登录/i })
    const registerLink = screen.getByRole('link', { name: /注册/i })
    
    expect(loginLink).toBeInTheDocument()
    expect(registerLink).toBeInTheDocument()
    
    expect(loginLink).toHaveAttribute('href', '/login')
    expect(registerLink).toHaveAttribute('href', '/register')
  })

  it('has correct styling classes for glass effect', () => {
    renderNavbar()
    const nav = screen.getByRole('navigation')
    
    expect(nav).toHaveClass('bg-white/70')
    expect(nav).toHaveClass('backdrop-blur-lg')
  })

  it('is fixed at the top of the page', () => {
    renderNavbar()
    const nav = screen.getByRole('navigation')
    
    expect(nav).toHaveClass('fixed')
    expect(nav).toHaveClass('top-0')
  })
}) 