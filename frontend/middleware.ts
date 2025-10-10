/**
 * middleware.ts - Middleware de Next.js para protección de rutas
 * 
 * Protege rutas privadas verificando la presencia de tokens de autenticación
 * Redirige a login si el usuario no está autenticado
 * Permite acceso a rutas públicas
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
 * Rutas privadas que requieren autenticación
 * Si el usuario intenta acceder sin token, será redirigido a /login
 */
const rutasPrivadas = ['/dashboard', '/upload', '/profile', '/settings', '/plants', '/diseases']

/**
 * Verifica si una ruta es pública
 * 
 * @param pathname - Ruta actual
 * @returns true si la ruta es pública
 */
function esRutaPublica(pathname: string): boolean {
  return rutasPublicas.some(ruta => pathname === ruta || pathname.startsWith(`${ruta}/`))
}

/**
 * Verifica si una ruta es privada
 * 
 * @param pathname - Ruta actual
 * @returns true si la ruta requiere autenticación
 */
function esRutaPrivada(pathname: string): boolean {
  return rutasPrivadas.some(ruta => pathname.startsWith(ruta))
}

/**
 * Middleware que protege rutas privadas
 * 
 * Flujo:
 * 1. Verifica si la ruta es pública → permite acceso
 * 2. Verifica si la ruta es privada y hay token → permite acceso
 * 3. Verifica si la ruta es privada sin token → redirige a /login
 * 4. Rutas no clasificadas → permite acceso (archivos estáticos, etc.)
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Permitir acceso a rutas públicas sin verificar autenticación
  if (esRutaPublica(pathname)) {
    return NextResponse.next()
  }

  // Verificar autenticación para rutas privadas
  if (esRutaPrivada(pathname)) {
    // Intentar obtener token de cookies o headers
    const token = request.cookies.get('access_token')?.value

    // Si no hay token, redirigir a login
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      // Guardar la URL original para redirigir después del login
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Si hay token, permitir acceso
    return NextResponse.next()
  }

  // Para rutas no clasificadas (archivos estáticos, API, etc.), permitir acceso
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
