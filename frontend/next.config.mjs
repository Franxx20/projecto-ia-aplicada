/**
 * Configuración de Next.js para Asistente Plantitas
 * 
 * Configuración optimizada para:
 * - Ejecución en Docker
 * - Integración con Backend FastAPI
 * - Build de producción optimizado
 * - Variables de entorno configuradas
 * 
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  // Output standalone para Docker (optimiza el tamaño de la imagen)
  output: 'standalone',

  // Configuración de variables de entorno públicas
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: 'Asistente Plantitas',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },

  // Configuración de imágenes
  images: {
    // Dominios permitidos para Next/Image
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: '*.blob.core.windows.net', // Azure Blob Storage
      },
    ],
    // Formatos de imagen soportados
    formats: ['image/webp', 'image/avif'],
  },

  // Configuración de headers para CORS y seguridad
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: process.env.NEXT_PUBLIC_API_URL || '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' },
        ],
      },
    ];
  },

  // Rewrites para proxy al backend (opcional, útil para desarrollo)
  async rewrites() {
    // Usar INTERNAL_API_URL si está disponible (dentro de Docker)
    // Si no, usar NEXT_PUBLIC_API_URL (desarrollo local)
    const apiUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    console.log('🔗 Next.js rewrites configurado para:', apiUrl);
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },

  // Configuración de TypeScript
  typescript: {
    // En producción, no ignorar errores de TypeScript
    ignoreBuildErrors: false,
  },

  // Configuración de ESLint
  eslint: {
    // En producción, no ignorar errores de ESLint
    ignoreDuringBuilds: false,
  },

  // Configuración experimental (Next.js 15)
  experimental: {
    // Optimización de CSS desactivada temporalmente por conflicto con critters
    // optimizeCss: true,
    
    // Server Actions (útil para formularios)
    serverActions: {
      allowedOrigins: ['localhost:4200', 'localhost:8000'],
    },
  },

  // Configuración de build
  compiler: {
    // Eliminar console.logs en producción
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },

  // Configuración de redirecciones
  async redirects() {
    return [
      // Redireccionar /home a /dashboard si el usuario está autenticado
      // Esto se puede manejar mejor con middleware
    ];
  },

  // Configuración de Webpack (si necesitas customizar)
  webpack: (config, { isServer }) => {
    // Configuración personalizada de webpack aquí si es necesario
    return config;
  },
};

export default nextConfig;
