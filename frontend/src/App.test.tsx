import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

/**
 * Suite de tests para el componente principal App
 * Verifica que la landing page se renderice correctamente
 */
describe('App Component', () => {
  it('debería renderizar el componente sin errores', () => {
    render(<App />)
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })

  it('debería mostrar el mensaje de bienvenida', () => {
    render(<App />)
    expect(screen.getByText('Bienvenido al Proyecto IA Aplicada')).toBeInTheDocument()
  })

  it('debería mostrar información del stack tecnológico', () => {
    render(<App />)
    expect(screen.getByText('React + TypeScript + Vite')).toBeInTheDocument()
    expect(screen.getByText('FastAPI + PostgreSQL')).toBeInTheDocument()
  })

  it('debería tener la estructura correcta con clases de Tailwind', () => {
    const { container } = render(<App />)
    const mainDiv = container.querySelector('.min-h-screen')
    expect(mainDiv).toBeInTheDocument()
    expect(mainDiv).toHaveClass('bg-gradient-to-br')
  })

  it('debería mostrar el título con gradiente', () => {
    render(<App />)
    const titulo = screen.getByText('Hello World')
    expect(titulo).toHaveClass('text-transparent', 'bg-clip-text', 'bg-gradient-to-r')
  })

  it('debería contener dos tarjetas de información (Frontend y Backend)', () => {
    render(<App />)
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('Backend')).toBeInTheDocument()
  })

  it('debería mostrar el mensaje del footer', () => {
    render(<App />)
    expect(screen.getByText(/Proyecto creado con las mejores prácticas/i)).toBeInTheDocument()
  })
})
