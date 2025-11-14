/**
 * middleware.ts - Middleware de Next.js para protección de rutas
 * 
 * NOTA: La verificación de autenticación real se maneja en el cliente con AuthContext
 * Este middleware solo previene acceso directo a rutas privadas sin considerar
 * el estado de autenticación del lado del servidor (ya que usamos localStorage)
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Rutas públicas que no requieren autenticación
 */
const rutasPublicas = ['/', '/login', '/register']

/**
 * Middleware simplificado que permite que AuthContext maneje la autenticación
 * 
 * Flujo:
 * 1. Permite acceso a todas las rutas (la protección real está en los componentes)
 * 2. AuthContext redirigirá al login si es necesario
 * 3. Los componentes verifican estaAutenticado antes de renderizar
 */
export function middleware(request: NextRequest) {
  // Permitir acceso a todas las rutas
  // La protección real se maneja en el cliente con AuthContext
  return NextResponse.next()
}

/**
 * Configuración del middleware
 * Define qué rutas serán procesadas por el middleware
 */
export const config = {
  matcher: [
    /*
     * Procesar todas las rutas excepto:
     * - API routes (/api/*)
     * - Archivos estáticos (_next/static/*)
     * - Archivos de imagen (_next/image/*)
     * - Favicon, robots.txt, etc.
     */
    '/((?!api|_next/static|_next/image|favicon.ico|robots.txt).*)',
  ],
}
