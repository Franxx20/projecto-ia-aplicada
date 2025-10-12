# DIRECTIVA PRINCIPAL
Evita trabajar en más de un archivo a la vez.
Edición simultánea de varios archivos puede causar corrupción.
Conversa y enseña sobre lo que haces mientras programas.

# Arquitectura: MVC
Backend: FastApi, sqlalchemy Como ORM
Frontend: Next.js + React + Typescript + Tailwind
Database: Postgresql (dev/prod)
IA: Claude Sonnet 4

# Estructura de Carpetas
```
/backend
  /app
    /api          # Rutas y endpoints
    /core         # Configuración, seguridad, dependencies
    /db           # Modelos de base de datos
    /schemas      # Pydantic models para validación
    /services     # Lógica de negocio
    /utils        # Utilidades y helpers
/frontend
  /src
    /components   # Componentes reutilizables
    /pages        # Páginas/Vistas principales
    /services     # Servicios y lógica de negocio
    /hooks        # Custom hooks de React
    /context      # Context API para estado global
    /models       # Interfaces y tipos TypeScript
    /utils        # Utilidades del frontend
    /assets       # Recursos estáticos
/tests
  /backend       # Tests de Python
  /frontend      # Tests de React/TypeScript
  /e2e          # Tests end-to-end con Cypress
```

# Nomenclatura:
Utilizar la nomenclatura tradicional de cada lenguaje/framework. Las funciones tienen que estar en español.

## Convenciones Específicas:
- **Python**: snake_case para funciones y variables, PascalCase para clases
- **TypeScript/React**: camelCase para variables y funciones, PascalCase para componentes y clases
- **Archivos**: kebab-case para nombres de archivos y carpetas, PascalCase para componentes React
- **Rutas API**: kebab-case (/usuarios/crear-perfil)
- **Variables de entorno**: UPPER_SNAKE_CASE

# Comentarios:
Agregar comentarios claros y concisos en el código

## Estándares de Documentación:
- **Python**: Docstrings con formato Google Style
- **TypeScript**: JSDoc para funciones complejas
- **React**: Comentarios descriptivos en componentes complejos y PropTypes/TypeScript interfaces
- **README**: Mantener documentación de setup y deployment actualizada

# Idioma: 
Siempre responde y pregunta en español

# Seguridad:
- Validar TODAS las entradas del usuario
- Usar Pydantic para validación de schemas
- Implementar autenticación JWT
- Variables sensibles SOLO en .env (nunca en código)
- Sanitizar datos antes de queries SQL
- Usar CORS correctamente configurado

# Manejo de Errores:
- Implementar middleware de manejo de errores global
- Logs detallados para debugging (no en producción)
- Respuestas de error consistentes en formato JSON
- Try-catch apropiados en operaciones asíncronas
- Validación de tipos en TypeScript estricta

# Base de Datos:
- Usar migraciones de Alembic para cambios de schema
- Indices apropiados para consultas frecuentes
- Relaciones definidas claramente en modelos
- Queries optimizadas (evitar N+1 problems)
- Transacciones para operaciones críticas

# API Design:
- RESTful endpoints con verbos HTTP correctos
- Paginación para listas grandes
- Filtros y búsqueda cuando sea apropiado
- Documenta las apis con comentarios

# Frontend Guidelines:
- Componentes funcionales con TypeScript
- Custom hooks para lógica reutilizable
- Props tipadas con interfaces TypeScript
- Context API o state management library para estado global
- Observables y manejo asíncrono con async/await
- Code splitting y lazy loading cuando sea apropiado
- Memoization con useMemo y useCallback para optimización

## Patrones React Específicos:
- **Custom Hooks**: Extraer lógica reutilizable en hooks personalizados
- **Context API**: Para estado global y evitar prop drilling
- **React Hook Form**: Para manejo de formularios con validaciones
- **Error Boundaries**: Para manejo de errores en componentes
- **Suspense y Lazy**: Para code splitting y carga diferida
- **useEffect cleanup**: Limpiar efectos secundarios apropiadamente
- **TypeScript strict mode**: Tipado estricto en todo el proyecto

# Test:
Pytest para python unit testing
pytest-asyncio para probar rutas FastAPI (async)
Jest + React Testing Library para unit testing de React
Testing Library para testear componentes React
Cypress para end-to-end testing en el navegador

## Cobertura de Tests:
- Mínimo 80% de cobertura en lógica de negocio
- Tests unitarios para servicios y utils
- Tests de integración para endpoints API
- Tests de componentes para UI crítica
- Tests E2E para flujos principales de usuario

# Deployment:
- No me realices nada de esto hasta llegar a la parte de producción, pregunta primero.
- Dockerfiles optimizados para producción
- Variables de entorno para configuración
- Health checks en containers
- Logging estructurado para monitoreo
- CI/CD pipeline con tests automáticos

# Performance:
- Lazy loading donde sea apropiado
- Compression de assets estáticos
- Caching estratégico en API
- Optimización de queries de DB
- Monitoreo de performance en producción

# Refactor:
Refactorizar código repetido en funciones reutilizables
Refactorizar lógica compleja en funciones separadas

## Principios de Clean Code:
- Funciones pequeñas y con propósito único
- Nombres descriptivos para variables y funciones
- Evitar anidamiento profundo (max 3 niveles)
- DRY (Don't Repeat Yourself)
- SOLID principles en diseño de clases

# Git Workflow:
- utiliza el sistema de creacion de ramas de git llamado GITFLOW
- Commits descriptivos en español
- Feature branches para nuevas funcionalidades
- Pull requests con revisión de código
- No commits directos a main/master
- Conventional commits: feat:, fix:, docs:, etc.

# Modelo de ciclo de vida de desarrollo de software: 
- agile