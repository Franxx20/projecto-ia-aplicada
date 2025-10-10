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

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Leaf } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"

export default function LoginPage() {
  const router = useRouter()
  const { iniciarSesion, registrarse, estaAutenticado, estaCargando: authLoading } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState("")
  
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
   */
  useEffect(() => {
    if (estaAutenticado) {
      router.push('/dashboard')
    }
  }, [estaAutenticado, router])

  /**
   * Maneja el envío del formulario de login
   * Usa el AuthContext para iniciar sesión
   */
  const manejarLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      await iniciarSesion(loginData.email, loginData.password)
      // El AuthContext manejará la navegación
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    }
  }

  /**
   * Maneja el envío del formulario de registro
   * Usa el AuthContext para registrarse
   */
  const manejarRegistro = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      await registrarse(registerData.email, registerData.password, registerData.nombre)
      
      // Después de registrarse exitosamente, cambiar a modo login
      setIsLogin(true)
      setError("")
      // Opcional: mostrar mensaje de éxito
      alert('Registro exitoso. Por favor, inicie sesión.')
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
                <p className="text-xs text-muted-foreground">
                  Mínimo 8 caracteres, incluir mayúscula, minúscula y número
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
              {authLoading 
                ? "Procesando..." 
                : isLogin 
                  ? "Iniciar Sesión" 
                  : "Crear Cuenta"
              }
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
