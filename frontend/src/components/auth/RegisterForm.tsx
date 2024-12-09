import { useState } from 'react'
import { RegisterData } from '../../types/auth'

interface RegisterFormProps {
  onSubmit: (data: RegisterData) => void;
  error?: string;
  isLoading?: boolean;
}

interface RegisterFormData extends RegisterData {
  confirmPassword: string;
}

export function RegisterForm({ onSubmit, error, isLoading = false }: RegisterFormProps) {
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  const [validationErrors, setValidationErrors] = useState<Partial<RegisterFormData>>({})

  const validateForm = (): boolean => {
    const errors: Partial<RegisterFormData> = {}
    
    // 验证用户名
    if (!formData.username) {
      errors.username = '用户名是必填项'
    }
    
    // 验证邮箱
    if (!formData.email) {
      errors.email = '邮箱是必填项'
    } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(formData.email)) {
      errors.email = '请输入有效的邮箱地址'
    }
    
    // 验证密码
    if (!formData.password) {
      errors.password = '密码是必填项'
    } else if (formData.password.length < 8) {
      errors.password = '密码至少需要8个字符'
    }
    
    // 验证确认密码
    if (!formData.confirmPassword) {
      errors.confirmPassword = '请确认密码'
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = '两次输入的密码不匹配'
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const isValid = validateForm()
    if (isValid) {
      const { confirmPassword, ...submitData } = formData
      onSubmit(submitData)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    const errors: Partial<RegisterFormData> = { ...validationErrors }

    // 验证单个字段
    switch (name) {
      case 'email':
        if (!value) {
          errors.email = '邮箱是必填项'
        } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(value)) {
          errors.email = '请输入有效的邮箱地址'
        } else {
          delete errors.email
        }
        break
      case 'password':
        if (!value) {
          errors.password = '密码是必填项'
        } else if (value.length < 8) {
          errors.password = '密码至少需要8个字符'
        } else {
          delete errors.password
        }
        break
      case 'confirmPassword':
        if (!value) {
          errors.confirmPassword = '请确认密码'
        } else if (value !== formData.password) {
          errors.confirmPassword = '两次输入的密码不匹配'
        } else {
          delete errors.confirmPassword
        }
        break
      case 'username':
        if (!value) {
          errors.username = '用户名是必填项'
        } else {
          delete errors.username
        }
        break
    }

    setValidationErrors(errors)
  }

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">注册</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            用户名
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            onBlur={handleBlur}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            disabled={isLoading}
          />
          {validationErrors.username && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.username}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            邮箱
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            onBlur={handleBlur}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            disabled={isLoading}
          />
          {validationErrors.email && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            密码
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            onBlur={handleBlur}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            disabled={isLoading}
          />
          {validationErrors.password && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.password}</p>
          )}
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
            确认密码
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            onBlur={handleBlur}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            disabled={isLoading}
          />
          {validationErrors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.confirmPassword}</p>
          )}
        </div>

        {error && (
          <div className="text-red-600 text-sm text-center">{error}</div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
        >
          {isLoading ? '注册中...' : '注册'}
        </button>
      </form>
    </div>
  )
} 