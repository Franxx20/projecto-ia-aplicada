/**
 * useAuth - Hook personalizado para acceder al contexto de autenticación
 * 
 * Proporciona acceso simplificado al AuthContext
 * Valida que el hook se use dentro del AuthProvider
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { useContext } from 'react'
import { AuthContext } from '@/contexts/AuthContext'

/**
 * Hook para acceder al contexto de autenticación
 * 
 * @returns Objeto con estado y funciones de autenticación
 * @throws Error si se usa fuera del AuthProvider
 * 
 * @example
 * ```tsx
 * function MiComponente() {
 *   const { usuario, estaAutenticado, iniciarSesion, cerrarSesion } = useAuth()
 *   
 *   if (!estaAutenticado) {
 *     return <p>Por favor inicia sesión</p>
 *   }
 *   
 *   return (
 *     <div>
 *       <p>Bienvenido {usuario?.nombre}</p>
 *       <button onClick={cerrarSesion}>Cerrar Sesión</button>
 *     </div>
 *   )
 * }
 * ```
 */
export function useAuth() {
  const contexto = useContext(AuthContext)

  if (contexto === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }

  return contexto
}
