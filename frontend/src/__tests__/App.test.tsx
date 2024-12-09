import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

// Mock子组件
vi.mock('../components/layout/Navbar', () => ({
  Navbar: () => <div data-testid="mock-navbar">Navbar</div>
}))

vi.mock('../pages/Home', () => ({
  Home: () => <div data-testid="mock-home">Home</div>
}))

vi.mock('../components/auth/LoginForm', () => ({
  LoginForm: ({ onSubmit }: { onSubmit: (data: any) => void }) => (
    <div data-testid="mock-login-form" onClick={() => onSubmit({ email: 'test@example.com', password: 'password' })}>
      LoginForm
    </div>
  )
}))

vi.mock('../components/auth/RegisterForm', () => ({
  RegisterForm: ({ onSubmit }: { onSubmit: (data: any) => void }) => (
    <div data-testid="mock-register-form" onClick={() => onSubmit({ username: 'test', email: 'test@example.com', password: 'password' })}>
      RegisterForm
    </div>
  )
}))

describe('App', () => {
  it('renders navbar and home page by default', () => {
    render(<App />)
    
    expect(screen.getByTestId('mock-navbar')).toBeInTheDocument()
    expect(screen.getByTestId('mock-home')).toBeInTheDocument()
  })

  it('renders login form at /login route', () => {
    window.history.pushState({}, '', '/login')
    render(<App />)
    
    expect(screen.getByTestId('mock-login-form')).toBeInTheDocument()
  })

  it('renders register form at /register route', () => {
    window.history.pushState({}, '', '/register')
    render(<App />)
    
    expect(screen.getByTestId('mock-register-form')).toBeInTheDocument()
  })

  it('handles login submission', async () => {
    const consoleSpy = vi.spyOn(console, 'log')
    window.history.pushState({}, '', '/login')
    
    render(<App />)
    screen.getByTestId('mock-login-form').click()
    
    expect(consoleSpy).toHaveBeenCalledWith('Login:', {
      email: 'test@example.com',
      password: 'password'
    })
  })

  it('handles register submission', async () => {
    const consoleSpy = vi.spyOn(console, 'log')
    window.history.pushState({}, '', '/register')
    
    render(<App />)
    screen.getByTestId('mock-register-form').click()
    
    expect(consoleSpy).toHaveBeenCalledWith('Register:', {
      username: 'test',
      email: 'test@example.com',
      password: 'password'
    })
  })
}) 