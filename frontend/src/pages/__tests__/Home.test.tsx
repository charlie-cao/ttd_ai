import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Home } from '../Home'

describe('Home', () => {
  it('renders the main heading', () => {
    render(<Home />)
    
    expect(screen.getByText('TDD开发实践')).toBeInTheDocument()
    expect(screen.getByText('前后端分离演示')).toBeInTheDocument()
  })

  it('renders the description text', () => {
    render(<Home />)
    
    expect(screen.getByText(/这是一个使用React \+ FastAPI开发的全栈应用示例/)).toBeInTheDocument()
  })

  it('renders action buttons with correct links', () => {
    render(<Home />)
    
    const sourceCodeLink = screen.getByRole('link', { name: /查看源码/i })
    const apiDocsLink = screen.getByRole('link', { name: /api文档/i })
    
    expect(sourceCodeLink).toBeInTheDocument()
    expect(apiDocsLink).toBeInTheDocument()
    
    expect(sourceCodeLink).toHaveAttribute('href', 'https://github.com/charlie-cao/ttd_ai')
    expect(apiDocsLink).toHaveAttribute('href', '/docs')
  })

  it('has gradient background', () => {
    render(<Home />)
    
    const container = screen.getByTestId('home-container')
    expect(container).toHaveClass('bg-gradient-to-br')
    expect(container).toHaveClass('from-indigo-50')
    expect(container).toHaveClass('via-white')
    expect(container).toHaveClass('to-purple-50')
  })
}) 