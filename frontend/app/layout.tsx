import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { Toaster } from "@/components/ui/toaster";
import { ChatWidget } from "@/components/ChatWidget";

/**
 * Metadata de la aplicación
 * Configura SEO, Open Graph, Twitter Cards, etc.
 */
export const metadata: Metadata = {
  title: {
    default: "NatureTag - Identificación y Cuidado de Plantas con IA",
    template: "%s | NatureTag"
  },
  description: "Identifica tus plantas con IA, recibe consejos personalizados de cuidado y mantén un registro de tu jardín.",
  keywords: ["plantas", "jardinería", "identificación", "IA", "cuidado de plantas", "botánica"],
  authors: [{ name: "Equipo NatureTag" }],
  creator: "NatureTag",
  openGraph: {
    type: "website",
    locale: "es_ES",
    url: "https://naturetag.com",
    title: "NatureTag",
    description: "Tu asistente personal de jardinería con IA",
    siteName: "NatureTag",
  },
  twitter: {
    card: "summary_large_image",
    title: "NatureTag",
    description: "Tu asistente personal de jardinería con IA",
  },
  robots: {
    index: true,
    follow: true,
  },
};

/**
 * Root Layout - Componente principal de la aplicación
 * 
 * Define la estructura HTML base y los estilos globales.
 * Este componente envuelve todas las páginas de la aplicación.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head />
      <body className="min-h-screen bg-background font-sans antialiased">
        {/* Contenedor principal de la aplicación */}
        <div className="relative flex min-h-screen flex-col">
          {/* Provider de autenticación global */}
          <AuthProvider>
            {children}
            {/* Chat Widget flotante (solo visible para usuarios autenticados) */}
            <ChatWidget />
          </AuthProvider>
        </div>
        {/* Toaster para notificaciones globales */}
        <Toaster />
      </body>
    </html>
  );
}
