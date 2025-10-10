import React from 'react'
import { Button } from '@/components/ui/button'
import { Leaf, Camera, MessageSquare, ShoppingBag } from 'lucide-react'

/**
 * Componente de Landing Page principal
 * 
 * Muestra la página de bienvenida con:
 * - Hero section con título y call-to-action
 * - Features section con las funcionalidades principales
 * 
 * @returns JSX Element - Landing page completa
 */
export default function LandingPage(): React.ReactElement {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0 bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-green-950 dark:via-emerald-950 dark:to-teal-950">
          {/* Pattern overlay para dar textura */}
          <div className="absolute inset-0 opacity-10 pattern-bg"></div>
        </div>

        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <div className="flex justify-center mb-6 animate-fade-in">
            <div className="bg-primary/10 p-4 rounded-full">
              <Leaf className="w-16 h-16 text-primary" />
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-balance animate-fade-in-up">
            Your Personal Plant Care Assistant
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground mb-8 text-pretty leading-relaxed animate-fade-in-up animation-delay-200">
            Identifica plantas al instante, diagnostica enfermedades con IA y obtén consejos personalizados para tu jardín
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up animation-delay-400">
            <Button 
              size="lg" 
              className="text-lg"
              onClick={() => window.location.href = '/login'}
            >
              Comenzar
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="text-lg bg-transparent"
              onClick={() => window.location.href = '/dashboard'}
            >
              Ver Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-background">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16 text-balance">
            Todo lo que necesitas para cuidar tus plantas
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1: Identificación de Plantas */}
            <div className="text-center group hover:scale-105 transition-transform duration-300">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
                <Camera className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Identificación de Plantas</h3>
              <p className="text-muted-foreground leading-relaxed">
                Toma una foto e identifica instantáneamente cualquier especie de planta con visión potenciada por IA
              </p>
            </div>

            {/* Feature 2: Consejos de IA */}
            <div className="text-center group hover:scale-105 transition-transform duration-300">
              <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-accent/20 transition-colors">
                <MessageSquare className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Consejos de Cuidado con IA</h3>
              <p className="text-muted-foreground leading-relaxed">
                Obtén recomendaciones personalizadas de riego, iluminación y cuidado desde nuestro asistente IA
              </p>
            </div>

            {/* Feature 3: Detección de Enfermedades */}
            <div className="text-center group hover:scale-105 transition-transform duration-300">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
                <Leaf className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Detección de Enfermedades</h3>
              <p className="text-muted-foreground leading-relaxed">
                Detecta enfermedades tempranamente y obtén recomendaciones de tratamiento para salvar tus plantas
              </p>
            </div>

            {/* Feature 4: Tienda de Jardín */}
            <div className="text-center group hover:scale-105 transition-transform duration-300">
              <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-accent/20 transition-colors">
                <ShoppingBag className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Tienda de Jardín</h3>
              <p className="text-muted-foreground leading-relaxed">
                Encuentra los productos, semillas y tratamientos correctos para tus plantas específicas
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4 bg-background">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <Leaf className="w-8 h-8 text-primary" />
          </div>
          <p className="text-muted-foreground mb-2">
            © 2025 Plant Care Assistant. Todos los derechos reservados.
          </p>
          <p className="text-sm text-muted-foreground">
            Proyecto IA Aplicada - Desarrollado con React, TypeScript y FastAPI
          </p>
        </div>
      </footer>
    </div>
  )
}
