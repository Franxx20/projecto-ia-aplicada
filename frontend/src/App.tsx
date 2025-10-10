import React from 'react'

/**
 * Componente principal de la aplicación
 * Muestra una landing page básica con mensaje de bienvenida
 * 
 * @returns JSX Element - Landing page con "Hello World"
 */
function App(): React.ReactElement {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 max-w-2xl w-full text-center transform hover:scale-105 transition-transform duration-300">
        <h1 className="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
          Hello World
        </h1>
        <p className="text-gray-600 text-lg md:text-xl mb-6">
          Bienvenido al Proyecto IA Aplicada
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <div className="bg-blue-50 rounded-lg p-4 hover:bg-blue-100 transition-colors">
            <p className="text-sm text-gray-500 mb-1">Frontend</p>
            <p className="font-semibold text-blue-600">React + TypeScript + Vite</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 hover:bg-purple-100 transition-colors">
            <p className="text-sm text-gray-500 mb-1">Backend</p>
            <p className="font-semibold text-purple-600">FastAPI + PostgreSQL</p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-400">
            🚀 Proyecto creado con las mejores prácticas de desarrollo
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
