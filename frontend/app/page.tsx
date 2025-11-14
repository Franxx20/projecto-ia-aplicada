/**
 * Página principal de NatureTag
 * Landing page con información general y acceso a la aplicación
 * 
 * Redirige automáticamente al dashboard si el usuario ya está autenticado
 */

"use client"

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Leaf, Camera, MessageSquare, ShoppingBag, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function HomePage() {
  const { estaAutenticado, estaCargando } = useAuth();
  const router = useRouter();

  // Redirigir al dashboard si ya está autenticado
  useEffect(() => {
    if (!estaCargando && estaAutenticado) {
      console.log("✅ Usuario ya autenticado, redirigiendo al dashboard...");
      router.push("/dashboard");
    }
  }, [estaAutenticado, estaCargando, router]);

  // Mostrar loader mientras verifica la sesión
  if (estaCargando) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  // Si está autenticado, no mostrar la landing (el useEffect redirigirá)
  if (estaAutenticado) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Redirigiendo al dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col w-full">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between max-w-7xl">
          <div className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">NatureTag</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Iniciar Sesión</Button>
            </Link>
            <Link href="/login?mode=register">
              <Button>Registrarse</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full flex flex-col items-center justify-center gap-6 pb-8 pt-6 md:py-16 lg:py-20 px-4 sm:px-6 lg:px-8">
        <div className="flex max-w-[980px] w-full flex-col items-center gap-4 text-center mx-auto">
          <h1 className="text-4xl font-bold leading-tight tracking-tighter md:text-6xl lg:text-7xl">
            Tu asistente personal
            <br className="hidden sm:inline" />
            {" "}de jardinería con{" "}
            <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              IA
            </span>
          </h1>
          <p className="max-w-[700px] text-lg text-muted-foreground sm:text-xl leading-relaxed">
            Identifica plantas, recibe consejos personalizados y mantén un registro
            completo de tu jardín. Todo con la ayuda de inteligencia artificial.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-8 md:py-12 lg:py-16 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto grid justify-center gap-6 sm:grid-cols-2 lg:grid-cols-4 max-w-7xl">
          <Card className="w-full">
            <CardHeader>
              <Camera className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Identificación IA</CardTitle>
              <CardDescription>
                Identifica cualquier planta con solo una foto
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="w-full">
            <CardHeader>
              <MessageSquare className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Consejos Personalizados</CardTitle>
              <CardDescription>
                Chat inteligente para responder tus dudas de jardinería
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="w-full">
            <CardHeader>
              <Leaf className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Diagnóstico</CardTitle>
              <CardDescription>
                Detecta enfermedades y plagas en tus plantas
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="w-full">
            <CardHeader>
              <ShoppingBag className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Marketplace</CardTitle>
              <CardDescription>
                Encuentra productos recomendados para tu jardín
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-8 md:py-12 lg:py-16 border-t px-4 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-[58rem] flex-col items-center justify-center gap-4 text-center">
          <h2 className="text-3xl font-bold leading-[1.1] sm:text-3xl md:text-5xl">
            ¿Listo para comenzar?
          </h2>
          <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
            Únete a miles de jardineros que ya usan NatureTag para cuidar
            mejor de sus plantas.
          </p>
          <Link href="/login?mode=register">
            <Button size="lg" className="gap-2">
              Crear Cuenta Gratis
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-6 md:py-8 w-full">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-between gap-4 md:flex-row max-w-7xl">
          <div className="flex items-center gap-2">
            <Leaf className="h-5 w-5 text-primary" />
            <p className="text-sm text-muted-foreground">
              © 2025 NatureTag. Todos los derechos reservados.
            </p>
          </div>
          <div className="flex gap-4">
            <Link href="/about" className="text-sm text-muted-foreground hover:underline">
              Acerca de
            </Link>
            <Link href="/privacy" className="text-sm text-muted-foreground hover:underline">
              Privacidad
            </Link>
            <Link href="/terms" className="text-sm text-muted-foreground hover:underline">
              Términos
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
