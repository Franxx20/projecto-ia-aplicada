"use client"

/**
 * Página de Login y Registro
 * 
 * Componente que permite a los usuarios iniciar sesión o registrarse
 * Conecta con el backend FastAPI para autenticación JWT
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Leaf } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
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
   * Maneja el envío del formulario de login
   * Conecta con /auth/login del backend FastAPI
   */
  const manejarLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al iniciar sesión')
      }

      const data = await response.json()
      
      // Guardar token en localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      // Redirigir al dashboard
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Maneja el envío del formulario de registro
   * Conecta con /auth/register del backend FastAPI
   */
  const manejarRegistro = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al registrarse')
      }

      await response.json()
      
      // Después de registrarse exitosamente, cambiar a modo login
      setIsLogin(true)
      setError("")
      // Opcional: mostrar mensaje de éxito
      alert('Registro exitoso. Por favor, inicie sesión.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrarse')
    } finally {
      setLoading(false)
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
                  disabled={loading}
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
                disabled={loading}
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
                disabled={loading}
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
            <Button className="w-full" size="lg" type="submit" disabled={loading}>
              {loading 
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
