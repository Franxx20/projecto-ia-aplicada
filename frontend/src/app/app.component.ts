import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <div class="min-h-screen bg-gray-50">
      <!-- Navigation Header -->
      <nav class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center">
              <h1 class="text-xl font-semibold text-primary-600">
                🌱 Plantitas AI
              </h1>
            </div>
            <div class="flex items-center space-x-4">
              <button class="btn-primary">
                Iniciar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- Main Content -->
      <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            Bienvenido a Plantitas AI
          </h2>
          <p class="text-lg text-gray-600 mb-8">
            Tu asistente inteligente para identificar plantas
          </p>
          <div class="card max-w-md mx-auto">
            <div class="card-body">
              <h3 class="text-xl font-semibold mb-4">¿Listo para comenzar?</h3>
              <p class="text-gray-600 mb-6">
                Sube una foto de tu planta y descubre información detallada sobre ella.
              </p>
              <button class="btn-primary w-full">
                Subir Imagen
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="bg-white border-t border-gray-200 mt-12">
        <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p class="text-center text-sm text-gray-500">
            © 2024 Plantitas AI. Proyecto de identificación de plantas con IA.
          </p>
        </div>
      </footer>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = "Plantitas AI";
}
