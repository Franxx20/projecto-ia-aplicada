"use client"

/**
 * Página del Dashboard
 * 
 * Dashboard principal protegido que solo es accesible después de iniciar sesión
 * Muestra información básica del usuario y opciones de navegación
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Leaf, LogOut, User } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"

export default function DashboardPage() {
  const router = useRouter()
  const { usuario, estaAutenticado, estaCargando, cerrarSesion } = useAuth()

  /**
   * Redirigir a login si no está autenticado
   * El middleware ya debería manejar esto, pero agregamos una capa extra de seguridad
   */
  useEffect(() => {
    if (!estaCargando && !estaAutenticado) {
      router.push('/login')
    }
  }, [estaAutenticado, estaCargando, router])

  /**
   * Maneja el cierre de sesión
   * Llama al método cerrarSesion del AuthContext
   */
  const manejarCerrarSesion = async () => {
    try {
      await cerrarSesion()
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    }
  }

  // Mostrar loading mientras se verifica la autenticación
  if (estaCargando) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Leaf className="h-12 w-12 text-primary animate-pulse mx-auto mb-4" />
          <p className="text-muted-foreground">Cargando...</p>
        </div>
      </div>
    )
  }

  // No mostrar nada si no está autenticado (se está redirigiendo)
  if (!estaAutenticado || !usuario) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Asistente Plantitas</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <User className="h-4 w-4" />
              <span className="text-muted-foreground">{usuario.nombre}</span>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={manejarCerrarSesion}
              className="gap-2"
            >
              <LogOut className="h-4 w-4" />
              Cerrar Sesión
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Welcome Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl">¡Hola, {usuario.nombre}! 👋</CardTitle>
              <CardDescription>
                Bienvenido a tu dashboard de Asistente Plantitas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-lg font-semibold">Hello World</p>
                <p className="text-muted-foreground">
                  Este es tu espacio personal para gestionar tus plantas y recibir consejos personalizados.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* User Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>Información de tu cuenta</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Email:</span>
                <span className="font-medium">{usuario.email}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Nombre:</span>
                <span className="font-medium">{usuario.nombre}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Estado:</span>
                <span className={`font-medium ${usuario.es_activo ? 'text-green-600' : 'text-red-600'}`}>
                  {usuario.es_activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Fecha de registro:</span>
                <span className="font-medium">
                  {new Date(usuario.fecha_registro).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
