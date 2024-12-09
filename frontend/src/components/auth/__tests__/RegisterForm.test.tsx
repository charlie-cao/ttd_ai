import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RegisterForm } from '../RegisterForm'

describe('RegisterForm', () => {
  it('renders register form with all necessary fields', () => {
    render(<RegisterForm onSubmit={() => {}} />)
    
    // 检查表单标题
    expect(screen.getByRole('heading', { name: /注册/i })).toBeInTheDocument()
    
    // 检查用户名输入框
    expect(screen.getByLabelText(/用户名/i)).toBeInTheDocument()
    
    // 检查邮箱输入框
    expect(screen.getByLabelText(/邮箱/i)).toBeInTheDocument()
    
    // 检查密码输入框
    expect(screen.getByLabelText(/^密码$/i)).toBeInTheDocument()
    
    // 检查确认密码输入框
    expect(screen.getByLabelText(/确认密码/i)).toBeInTheDocument()
    
    // 检查提交按钮
    expect(screen.getByRole('button', { name: /注册/i })).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    render(<RegisterForm onSubmit={() => {}} />)
    
    // 点击提交按钮但不填写任何字段
    fireEvent.click(screen.getByRole('button', { name: /注册/i }))
    
    // 等待并检查错误消息
    await waitFor(() => {
      expect(screen.getByText(/用户名是必填项/i)).toBeInTheDocument()
      expect(screen.getByText(/邮箱是必填项/i)).toBeInTheDocument()
      expect(screen.getByText(/密码是必填项/i)).toBeInTheDocument()
      expect(screen.getByText(/请确认密码/i)).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    render(<RegisterForm onSubmit={() => {}} />)
    
    // 输入无效的邮箱格式并提交
    const emailInput = screen.getByLabelText(/邮箱/i)
    await userEvent.type(emailInput, 'invalid-email')
    fireEvent.blur(emailInput)
    
    // 检查错误消息
    await waitFor(() => {
      expect(screen.getByText(/请输入有效的邮箱地址/i)).toBeInTheDocument()
    })
  })

  it('validates password match', async () => {
    render(<RegisterForm onSubmit={() => {}} />)
    
    // 输入不匹配的密码
    await userEvent.type(screen.getByLabelText(/^密码$/i), 'password123')
    await userEvent.type(screen.getByLabelText(/确认密码/i), 'password456')
    fireEvent.blur(screen.getByLabelText(/确认密码/i))
    
    // 检查错误消息
    await waitFor(() => {
      expect(screen.getByText(/两次输入的密码不匹配/i)).toBeInTheDocument()
    })
  })

  it('validates password strength', async () => {
    render(<RegisterForm onSubmit={() => {}} />)
    
    // 输入弱密码
    const passwordInput = screen.getByLabelText(/^密码$/i)
    await userEvent.type(passwordInput, 'weak')
    fireEvent.blur(passwordInput)
    
    // 检查错误消息
    await waitFor(() => {
      expect(screen.getByText(/密码至少需要8个字符/i)).toBeInTheDocument()
    })
  })

  it('calls onSubmit with form data when submitted with valid data', async () => {
    const mockSubmit = vi.fn()
    render(<RegisterForm onSubmit={mockSubmit} />)
    
    // 填写表单
    await userEvent.type(screen.getByLabelText(/用户名/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/邮箱/i), 'test@example.com')
    await userEvent.type(screen.getByLabelText(/^密码$/i), 'password123')
    await userEvent.type(screen.getByLabelText(/确认密码/i), 'password123')
    
    // 提交表单
    fireEvent.click(screen.getByRole('button', { name: /注册/i }))
    
    // 验证onSubmit被调用，且参数正确
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123'
      })
    })
  })

  it('shows error message when registration fails', () => {
    const errorMessage = '用户名已被注册'
    render(<RegisterForm onSubmit={() => {}} error={errorMessage} />)
    
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('disables submit button while loading', () => {
    render(<RegisterForm onSubmit={() => {}} isLoading={true} />)
    
    expect(screen.getByRole('button', { name: /注册中.../i })).toBeDisabled()
  })
}) 