import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import LandingPage from './LandingPage'

describe('LandingPage', () => {
  /**
   * Test: Verifica que el componente LandingPage se renderiza sin errores
   */
  it('debe renderizar el componente sin errores', () => {
    render(<LandingPage />)
    expect(screen.getByText(/Your Personal Plant Care Assistant/i)).toBeInTheDocument()
  })

  /**
   * Test: Verifica que el Hero Section contiene el título principal
   */
  it('debe mostrar el título principal en el Hero Section', () => {
    render(<LandingPage />)
    const heading = screen.getByRole('heading', { name: /Your Personal Plant Care Assistant/i })
    expect(heading).toBeInTheDocument()
  })

  /**
   * Test: Verifica que el Hero Section contiene la descripción
   */
  it('debe mostrar la descripción del servicio', () => {
    render(<LandingPage />)
    expect(screen.getByText(/Identifica plantas al instante/i)).toBeInTheDocument()
  })

  /**
   * Test: Verifica que los botones de call-to-action están presentes
   */
  it('debe mostrar los botones de CTA (Comenzar y Ver Demo)', () => {
    render(<LandingPage />)
    expect(screen.getByRole('button', { name: /Comenzar/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Ver Demo/i })).toBeInTheDocument()
  })

  /**
   * Test: Verifica que la sección de Features contiene el título
   */
  it('debe mostrar el título de la sección Features', () => {
    render(<LandingPage />)
    expect(screen.getByText(/Todo lo que necesitas para cuidar tus plantas/i)).toBeInTheDocument()
  })

  /**
   * Test: Verifica que las 4 features principales están presentes
   */
  it('debe mostrar las 4 features principales', () => {
    render(<LandingPage />)
    
    // Feature 1: Identificación de Plantas
    expect(screen.getByText('Identificación de Plantas')).toBeInTheDocument()
    expect(screen.getByText(/Toma una foto e identifica/i)).toBeInTheDocument()

    // Feature 2: Consejos de Cuidado con IA
    expect(screen.getByText('Consejos de Cuidado con IA')).toBeInTheDocument()
    expect(screen.getByText(/Obtén recomendaciones personalizadas/i)).toBeInTheDocument()

    // Feature 3: Detección de Enfermedades
    expect(screen.getByText('Detección de Enfermedades')).toBeInTheDocument()
    expect(screen.getByText(/Detecta enfermedades tempranamente/i)).toBeInTheDocument()

    // Feature 4: Tienda de Jardín
    expect(screen.getByText('Tienda de Jardín')).toBeInTheDocument()
    expect(screen.getByText(/Encuentra los productos/i)).toBeInTheDocument()
  })

  /**
   * Test: Verifica que el Footer está presente con la información correcta
   */
  it('debe mostrar el footer con información del proyecto', () => {
    render(<LandingPage />)
    expect(screen.getByText(/© 2025 Plant Care Assistant/i)).toBeInTheDocument()
    expect(screen.getByText(/Proyecto IA Aplicada/i)).toBeInTheDocument()
  })

  /**
   * Test: Verifica que los iconos de lucide-react se renderizan
   */
  it('debe renderizar los iconos de features', () => {
    const { container } = render(<LandingPage />)
    // Verificamos que existen elementos SVG (iconos de lucide-react)
    const svgElements = container.querySelectorAll('svg')
    expect(svgElements.length).toBeGreaterThan(0)
  })

  /**
   * Test: Verifica la estructura responsive con clases de Tailwind
   */
  it('debe tener clases responsive de Tailwind CSS', () => {
    const { container } = render(<LandingPage />)
    const mainContainer = container.querySelector('.min-h-screen')
    expect(mainContainer).toBeInTheDocument()
  })
})
