/**
 * Página principal de Asistente Plantitas
 * Landing page con información general y acceso a la aplicación
 */

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Leaf, Camera, MessageSquare, ShoppingBag } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Asistente Plantitas</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Iniciar Sesión</Button>
            </Link>
            <Link href="/login">
              <Button>Comenzar</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container flex flex-col items-center justify-center gap-6 pb-8 pt-6 md:py-10">
        <div className="flex max-w-[980px] flex-col items-center gap-2 text-center">
          <h1 className="text-4xl font-bold leading-tight tracking-tighter md:text-6xl lg:text-7xl">
            Tu asistente personal
            <br className="hidden sm:inline" />
            {" "}de jardinería con{" "}
            <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              IA
            </span>
          </h1>
          <p className="max-w-[700px] text-lg text-muted-foreground sm:text-xl">
            Identifica plantas, recibe consejos personalizados y mantén un registro
            completo de tu jardín. Todo con la ayuda de inteligencia artificial.
          </p>
        </div>
        <div className="flex gap-4">
          <Link href="/login">
            <Button size="lg" className="gap-2">
              <Camera className="h-5 w-5" />
              Identificar Planta
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              Ver Demo
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-8 md:py-12 lg:py-24">
        <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-4">
          <Card>
            <CardHeader>
              <Camera className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Identificación IA</CardTitle>
              <CardDescription>
                Identifica cualquier planta con solo una foto
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Consejos Personalizados</CardTitle>
              <CardDescription>
                Chat inteligente para responder tus dudas de jardinería
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Leaf className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Diagnóstico</CardTitle>
              <CardDescription>
                Detecta enfermedades y plagas en tus plantas
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
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
      <section className="container py-8 md:py-12 lg:py-24 border-t">
        <div className="mx-auto flex max-w-[58rem] flex-col items-center justify-center gap-4 text-center">
          <h2 className="text-3xl font-bold leading-[1.1] sm:text-3xl md:text-5xl">
            ¿Listo para comenzar?
          </h2>
          <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
            Únete a miles de jardineros que ya usan Asistente Plantitas para cuidar
            mejor de sus plantas.
          </p>
          <Link href="/login">
            <Button size="lg" className="gap-2">
              Crear Cuenta Gratis
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <div className="flex items-center gap-2">
            <Leaf className="h-5 w-5 text-primary" />
            <p className="text-sm text-muted-foreground">
              © 2025 Asistente Plantitas. Todos los derechos reservados.
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
