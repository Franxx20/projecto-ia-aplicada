"use client"

/**
 * Página de Login y Registro
 * 
 * Componente que permite a los usuarios iniciar sesión o registrarse
 * Usa AuthContext para manejar la autenticación de forma centralizada
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { useState, useEffect, Suspense } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Leaf } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"

function LoginPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { iniciarSesion, registrarse, cerrarSesion, estaAutenticado, estaCargando: authLoading } = useAuth()
  
  // Detectar el modo desde la URL: /login?mode=register
  const modeParam = searchParams?.get('mode')
  const [isLogin, setIsLogin] = useState(modeParam !== 'register')
  const [error, setError] = useState("")
  const [mostrarRedireccion, setMostrarRedireccion] = useState(false)
  const [intentandoRedirigir, setIntentandoRedirigir] = useState(false)
  
  // Formulario de login
  const [loginData, setLoginData] = useState({
    email: "",
    password: ""
  })
  
  // Formulario de registro
  const [registerData, setRegisterData] = useState({
    email: "",
    password: "",
    nombre: ""
  })

  /**
   * Redirigir al dashboard si ya está autenticado
   * SOLO si NO estamos en proceso de carga inicial Y NO estamos intentando redirigir
   */
  useEffect(() => {
    // Esperar a que termine la carga inicial del AuthContext
    // Solo redirigir automáticamente si ya estaba autenticado desde antes (no por login reciente)
    if (!authLoading && estaAutenticado && !intentandoRedirigir) {
      console.log('Usuario ya autenticado desde antes, redirigiendo al dashboard...')
      setMostrarRedireccion(true)
      // Dar tiempo para mostrar el mensaje antes de redirigir
      const timer = setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [estaAutenticado, authLoading, router, intentandoRedirigir])

  /**
   * Si el usuario ya está autenticado, mostrar pantalla de redirección
   */
  if (mostrarRedireccion) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-secondary/20 to-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-primary/10 p-3 rounded-full">
                <Leaf className="w-10 h-10 text-primary" />
              </div>
            </div>
            <CardTitle className="text-2xl">Ya estás autenticado</CardTitle>
            <CardDescription>
              Redirigiendo al dashboard...
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-muted-foreground">
              Si no deseas continuar con esta sesión, puedes{' '}
              <button 
                onClick={async () => {
                  await cerrarSesion()
                  setMostrarRedireccion(false)
                }}
                className="text-primary hover:underline font-medium"
                type="button"
              >
                cerrar sesión aquí
              </button>
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  /**
   * Maneja el envío del formulario de login
   * Usa el AuthContext para iniciar sesión
   */
  const manejarLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIntentandoRedirigir(true)

    try {
      await iniciarSesion(loginData.email, loginData.password)
      console.log('✅ Inicio de sesión exitoso, redirigiendo al dashboard...')
      // Redirigir inmediatamente después del login exitoso
      router.push('/dashboard')
    } catch (err) {
      console.error('❌ Error al iniciar sesión:', err)
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
      setIntentandoRedirigir(false)
    }
  }

  /**
   * Maneja el envío del formulario de registro
   * Usa el AuthContext para registrarse
   */
  const manejarRegistro = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Validación adicional en el frontend
    if (registerData.password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres")
      return
    }
    if (!/[A-Z]/.test(registerData.password)) {
      setError("La contraseña debe contener al menos una letra MAYÚSCULA")
      return
    }
    if (!/[a-z]/.test(registerData.password)) {
      setError("La contraseña debe contener al menos una letra minúscula")
      return
    }
    if (!/[0-9]/.test(registerData.password)) {
      setError("La contraseña debe contener al menos un número")
      return
    }

    try {
      await registrarse(registerData.email, registerData.password, registerData.nombre)
      
      // Después de registrarse exitosamente, cambiar a modo login
      setIsLogin(true)
      setError("")
      // Opcional: mostrar mensaje de éxito
      alert('✅ Registro exitoso. Por favor, inicie sesión con sus credenciales.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrarse')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-secondary/20 to-background">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-full">
              <Leaf className="w-10 h-10 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl">
            {isLogin ? "Bienvenido de Nuevo" : "Crear Cuenta"}
          </CardTitle>
          <CardDescription>
            {isLogin 
              ? "Inicia sesión para continuar cuidando tus plantas" 
              : "Comienza tu viaje en el cuidado de plantas hoy"
            }
          </CardDescription>
        </CardHeader>

        <form onSubmit={isLogin ? manejarLogin : manejarRegistro}>
          <CardContent className="space-y-4">
            {/* Mostrar errores */}
            {error && (
              <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            {/* Campo nombre (solo en registro) */}
            {!isLogin && (
              <div className="space-y-2">
                <Label htmlFor="nombre">Nombre Completo</Label>
                <Input 
                  id="nombre" 
                  placeholder="Juan Pérez"
                  value={registerData.nombre}
                  onChange={(e) => setRegisterData({...registerData, nombre: e.target.value})}
                  required={!isLogin}
                  disabled={authLoading}
                />
              </div>
            )}

            {/* Campo email */}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="tu@ejemplo.com"
                value={isLogin ? loginData.email : registerData.email}
                onChange={(e) => {
                  if (isLogin) {
                    setLoginData({...loginData, email: e.target.value})
                  } else {
                    setRegisterData({...registerData, email: e.target.value})
                  }
                }}
                required
                disabled={authLoading}
              />
            </div>

            {/* Campo contraseña */}
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••"
                value={isLogin ? loginData.password : registerData.password}
                onChange={(e) => {
                  if (isLogin) {
                    setLoginData({...loginData, password: e.target.value})
                  } else {
                    setRegisterData({...registerData, password: e.target.value})
                  }
                }}
                required
                disabled={authLoading}
              />
              {!isLogin && (
                <p className="text-xs text-muted-foreground mt-1">
                  <strong>Requisitos:</strong> Mínimo 8 caracteres, debe incluir:
                  <br />• Una letra MAYÚSCULA
                  <br />• Una letra minúscula
                  <br />• Un número
                </p>
              )}
            </div>

            {/* Link olvidé contraseña (solo en login) */}
            {isLogin && (
              <div className="text-right">
                <Link href="/forgot-password" className="text-sm text-primary hover:underline">
                  ¿Olvidaste tu contraseña?
                </Link>
              </div>
            )}

            {/* Botón submit */}
            <Button className="w-full" size="lg" type="submit" disabled={authLoading}>
              {authLoading && "Procesando..."}
              {!authLoading && isLogin && "Iniciar Sesión"}
              {!authLoading && !isLogin && "Crear Cuenta"}
            </Button>
          </CardContent>
        </form>

        <CardFooter className="flex-col space-y-4">
          <div className="text-sm text-center text-muted-foreground">
            {isLogin ? "¿No tienes una cuenta? " : "¿Ya tienes una cuenta? "}
            <button 
              onClick={() => {
                setIsLogin(!isLogin)
                setError("")
              }} 
              className="text-primary hover:underline font-medium"
              type="button"
            >
              {isLogin ? "Regístrate" : "Inicia sesión"}
            </button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Leaf className="w-12 h-12 animate-pulse text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Cargando...</p>
        </div>
      </div>
    }>
      <LoginPageContent />
    </Suspense>
  )
}
