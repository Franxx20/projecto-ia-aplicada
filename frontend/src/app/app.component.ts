import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div style="text-align: center; padding: 50px; background: #f0f0f0; min-height: 100vh;">
      <h1 style="color: #333; font-size: 48px; margin-bottom: 20px;">
        🤖 Proyecto IA Aplicada
      </h1>
      <h2 style="color: #666; font-size: 24px; margin-bottom: 30px;">
        ¡Aplicación funcionando correctamente!
      </h2>
      <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 500px;">
        <p style="font-size: 18px; margin-bottom: 20px;">
          ✅ Angular está ejecutándose
        </p>
        <p style="font-size: 18px; margin-bottom: 20px;">
          🚀 Hot reload activo
        </p>
        <p style="font-size: 18px; margin-bottom: 20px;">
          ⏰ Hora: {{ time }}
        </p>
        <hr style="margin: 20px 0;">
        <h3 style="margin-bottom: 15px;">Enlaces útiles:</h3>
        <p><a href="http://localhost:4200" style="color: #007bff;">Frontend (4200)</a></p>
        <p><a href="http://localhost:8000" style="color: #28a745;">Backend (8000)</a></p>
        <p><a href="http://localhost:8000/docs" style="color: #ffc107;">API Docs</a></p>
        <p><a href="http://localhost:8080" style="color: #6f42c1;">Admin BD</a></p>
      </div>
      <button 
        (click)="testBackend()" 
        style="background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 5px; font-size: 16px; cursor: pointer;"
        [disabled]="loading">
        {{ loading ? 'Probando...' : 'Probar Backend' }}
      </button>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'projecto-ia-aplicada';
  time = new Date().toLocaleTimeString();
  loading = false;

  constructor() {
    // Actualizar el tiempo cada segundo
    setInterval(() => {
      this.time = new Date().toLocaleTimeString();
    }, 1000);
  }

  async testBackend() {
    this.loading = true;
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        alert('✅ Backend conectado correctamente!');
      } else {
        alert('❌ Backend respondió con error: ' + response.status);
      }
    } catch (error) {
      alert('❌ No se pudo conectar al backend');
    } finally {
      this.loading = false;
    }
  }
}