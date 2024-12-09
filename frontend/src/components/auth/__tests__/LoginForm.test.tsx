import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from '../LoginForm'

describe('LoginForm', () => {
  it('renders login form with all necessary fields', () => {
    render(<LoginForm onSubmit={() => {}} />)
    
    // 检查表单标题
    expect(screen.getByRole('heading', { name: /登录/i })).toBeInTheDocument()
    
    // 检查用户名输入框
    expect(screen.getByLabelText(/用户名/i)).toBeInTheDocument()
    
    // 检查密码输入框
    expect(screen.getByLabelText(/密码/i)).toBeInTheDocument()
    
    // 检查提交按钮
    expect(screen.getByRole('button', { name: /登录/i })).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    render(<LoginForm onSubmit={() => {}} />)
    
    // 点击提交按钮但不填写任何字段
    fireEvent.click(screen.getByRole('button', { name: /登录/i }))
    
    // 等待并检查错误消息
    await waitFor(() => {
      expect(screen.getByText(/用户名是必填项/i)).toBeInTheDocument()
      expect(screen.getByText(/密码是必填项/i)).toBeInTheDocument()
    })
  })

  it('calls onSubmit with form data when submitted', async () => {
    const mockSubmit = vi.fn()
    render(<LoginForm onSubmit={mockSubmit} />)
    
    // 填写表单
    await userEvent.type(screen.getByLabelText(/用户名/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/密码/i), 'password123')
    
    // 提交表单
    fireEvent.click(screen.getByRole('button', { name: /登录/i }))
    
    // 验证onSubmit被调用，且参数正确
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      })
    })
  })

  it('shows error message when login fails', () => {
    const errorMessage = '用户名或密码错误'
    render(<LoginForm onSubmit={() => {}} error={errorMessage} />)
    
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('disables submit button while loading', () => {
    render(<LoginForm onSubmit={() => {}} isLoading={true} />)
    
    expect(screen.getByRole('button', { name: /登录中.../i })).toBeDisabled()
  })
}) 