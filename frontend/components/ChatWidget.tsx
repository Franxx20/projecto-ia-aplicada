/**
 * ChatWidget - Asistente de Jardinería flotante
 * 
 * Widget de chat flotante que aparece en todas las páginas autenticadas.
 * Permite a los usuarios hacer preguntas sobre jardinería y recibir
 * respuestas del LLM (Gemini AI) con contexto de sus plantas.
 * 
 * Features:
 * - Botón flotante en esquina inferior derecha
 * - Modal expandible con lista de conversaciones
 * - Chat en tiempo real con el asistente
 * - Soporte para contexto de planta específica
 * - Animaciones suaves y diseño adaptativo
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send, Plus, Trash2, Loader2, Leaf, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import chatService, { type Conversacion, type Mensaje } from '@/lib/chat.service'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

export function ChatWidget() {
  const { usuario, estaCargando: cargandoAuth } = useAuth()
  
  // Estados principales
  const [estaAbierto, setEstaAbierto] = useState(false)
  const [vistaActual, setVistaActual] = useState<'lista' | 'chat'>('lista')
  
  // Estados de conversaciones
  const [conversaciones, setConversaciones] = useState<Conversacion[]>([])
  const [conversacionActiva, setConversacionActiva] = useState<Conversacion | null>(null)
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  
  // Estados de input
  const [inputMensaje, setInputMensaje] = useState('')
  const [enviandoMensaje, setEnviandoMensaje] = useState(false)
  
  // Estados de carga
  const [cargandoConversaciones, setCargandoConversaciones] = useState(false)
  const [cargandoMensajes, setCargandoMensajes] = useState(false)
  
  // Refs
  const mensajesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // ==================== EFFECTS ====================
  
  // Scroll automático al final de mensajes
  const scrollToBottom = () => {
    mensajesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    if (mensajes.length > 0) {
      scrollToBottom()
    }
  }, [mensajes])
  
  // Cargar conversaciones al abrir
  useEffect(() => {
    if (estaAbierto && vistaActual === 'lista') {
      cargarConversaciones()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estaAbierto, vistaActual])
  
  // Enfocar input cuando se abre el chat
  useEffect(() => {
    if (estaAbierto && vistaActual === 'chat' && inputRef.current) {
      inputRef.current.focus()
    }
  }, [estaAbierto, vistaActual])
  
  // ==================== FUNCIONES ====================
  
  const cargarConversaciones = async () => {
    setCargandoConversaciones(true)
    try {
      const resultado = await chatService.obtenerConversaciones(0, 20, true)
      setConversaciones(resultado.conversaciones)
    } catch (error) {
      console.error('Error al cargar conversaciones:', error)
    } finally {
      setCargandoConversaciones(false)
    }
  }
  
  const cargarMensajes = async (conversacionId: number) => {
    setCargandoMensajes(true)
    try {
      const resultado = await chatService.obtenerMensajes(conversacionId, 0, 100)
      setMensajes(resultado.mensajes)
    } catch (error) {
      console.error('Error al cargar mensajes:', error)
    } finally {
      setCargandoMensajes(false)
    }
  }
  
  // No mostrar si el usuario no está autenticado
  if (!usuario || cargandoAuth) {
    return null
  }
  
  const crearNuevaConversacion = async () => {
    try {
      const nuevaConv = await chatService.crearConversacion()
      setConversacionActiva(nuevaConv)
      setMensajes([])
      setVistaActual('chat')
    } catch (error) {
      console.error('Error al crear conversación:', error)
    }
  }
  
  const seleccionarConversacion = async (conversacion: Conversacion) => {
    setConversacionActiva(conversacion)
    setVistaActual('chat')
    await cargarMensajes(conversacion.id)
  }
  
  const enviarMensaje = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputMensaje.trim() || !conversacionActiva) return
    
    const contenido = inputMensaje.trim()
    setInputMensaje('')
    setEnviandoMensaje(true)
    
    // Agregar mensaje optimista del usuario
    const mensajeTemp: Mensaje = {
      id: Date.now(),
      conversacion_id: conversacionActiva.id,
      rol: 'user',
      contenido,
      created_at: new Date().toISOString()
    }
    setMensajes(prev => [...prev, mensajeTemp])
    
    try {
      const respuesta = await chatService.enviarMensaje(
        conversacionActiva.id,
        contenido
      )
      
      // Reemplazar mensaje temporal con el real y agregar respuesta
      setMensajes(prev => {
        const sinTemp = prev.filter(m => m.id !== mensajeTemp.id)
        return [...sinTemp, respuesta.mensaje_usuario, respuesta.mensaje_asistente]
      })
      
      // Actualizar título si es la primera interacción
      if (mensajes.length === 0) {
        await cargarConversaciones()
      }
    } catch (error) {
      console.error('Error al enviar mensaje:', error)
      // Remover mensaje temporal en caso de error
      setMensajes(prev => prev.filter(m => m.id !== mensajeTemp.id))
    } finally {
      setEnviandoMensaje(false)
    }
  }
  
  const eliminarConversacion = async (conversacionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!confirm('¿Archivar esta conversación?')) return
    
    try {
      await chatService.eliminarConversacion(conversacionId, false)
      
      // Actualizar lista
      setConversaciones(prev => prev.filter(c => c.id !== conversacionId))
      
      // Si es la activa, volver a lista
      if (conversacionActiva?.id === conversacionId) {
        setConversacionActiva(null)
        setMensajes([])
        setVistaActual('lista')
      }
    } catch (error) {
      console.error('Error al eliminar conversación:', error)
    }
  }
  
  const volverALista = () => {
    setVistaActual('lista')
    setConversacionActiva(null)
    setMensajes([])
  }
  
  const toggleChat = () => {
    setEstaAbierto(!estaAbierto)
    if (!estaAbierto) {
      setVistaActual('lista')
    }
  }
  
  // ==================== RENDER ====================
  
  return (
    <>
      {/* Botón flotante */}
      <Button
        onClick={toggleChat}
        size="icon"
        className={cn(
          "fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full shadow-lg",
          "transition-all duration-300 hover:scale-110",
          "bg-gradient-to-r from-green-600 to-emerald-600",
          "hover:from-green-700 hover:to-emerald-700"
        )}
        aria-label="Abrir chat asistente"
      >
        {estaAbierto ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>
      
      {/* Modal del chat */}
      {estaAbierto && (
        <Card className={cn(
          "fixed bottom-24 right-6 z-40",
          "w-96 h-[600px]",
          "shadow-2xl border-2",
          "flex flex-col",
          "animate-in slide-in-from-bottom-5 duration-300"
        )}>
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-green-600 to-emerald-600 text-white">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              <h3 className="font-semibold">
                {vistaActual === 'lista' ? 'Asistente de Jardinería' : conversacionActiva?.titulo}
              </h3>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={toggleChat}
              className="text-white hover:bg-white/20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Contenido */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {vistaActual === 'lista' ? (
              <VistaLista
                conversaciones={conversaciones}
                cargando={cargandoConversaciones}
                onSeleccionar={seleccionarConversacion}
                onNueva={crearNuevaConversacion}
                onEliminar={eliminarConversacion}
              />
            ) : (
              <VistaChat
                mensajes={mensajes}
                cargando={cargandoMensajes}
                enviando={enviandoMensaje}
                inputMensaje={inputMensaje}
                onInputChange={setInputMensaje}
                onEnviar={enviarMensaje}
                onVolver={volverALista}
                inputReference={inputRef}
                mensajesEndReference={mensajesEndRef}
              />
            )}
          </div>
        </Card>
      )}
    </>
  )
}

// ==================== SUBCOMPONENTES ====================

function VistaLista({
  conversaciones,
  cargando,
  onSeleccionar,
  onNueva,
  onEliminar
}: {
  conversaciones: Conversacion[]
  cargando: boolean
  onSeleccionar: (conv: Conversacion) => void
  onNueva: () => void
  onEliminar: (id: number, e: React.MouseEvent) => void
}) {
  return (
    <>
      <div className="p-4 border-b">
        <Button
          onClick={onNueva}
          className="w-full gap-2"
          variant="default"
        >
          <Plus className="h-4 w-4" />
          Nueva Conversación
        </Button>
      </div>
      
      <ScrollArea className="flex-1">
        {cargando ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : conversaciones.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-center p-4">
            <Leaf className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
              No hay conversaciones aún.
              <br />
              ¡Comienza una nueva!
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {conversaciones.map((conv) => (
              <div
                key={conv.id}
                onClick={() => onSeleccionar(conv)}
                className={cn(
                  "p-3 rounded-lg cursor-pointer",
                  "hover:bg-accent transition-colors",
                  "flex items-start justify-between gap-2",
                  "border"
                )}
              >
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm truncate">
                    {conv.titulo}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {conv.total_mensajes} mensaje{conv.total_mensajes !== 1 ? 's' : ''}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={(e) => onEliminar(conv.id, e)}
                  className="shrink-0"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </>
  )
}

function VistaChat({
  mensajes,
  cargando,
  enviando,
  inputMensaje,
  onInputChange,
  onEnviar,
  onVolver,
  inputReference,
  mensajesEndReference
}: {
  mensajes: Mensaje[]
  cargando: boolean
  enviando: boolean
  inputMensaje: string
  onInputChange: (value: string) => void
  onEnviar: (e: React.FormEvent) => void
  onVolver: () => void
  inputReference: React.RefObject<HTMLInputElement>
  mensajesEndReference: React.RefObject<HTMLDivElement>
}) {
  return (
    <>
      <div className="p-3 border-b">
        <Button
          variant="ghost"
          size="sm"
          onClick={onVolver}
          className="gap-2"
        >
          ← Volver
        </Button>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        {cargando ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : mensajes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <Sparkles className="h-12 w-12 text-primary mb-4" />
            <h4 className="font-semibold mb-2">¡Hola! Soy tu asistente de jardinería 🌱</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Pregúntame sobre cuidados, riego, plagas, o cualquier duda sobre tus plantas.
            </p>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>💡 &quot;¿Cuándo debo regar mi Monstera?&quot;</p>
              <p>💡 &quot;¿Por qué las hojas están amarillas?&quot;</p>
              <p>💡 &quot;¿Qué fertilizante usar en primavera?&quot;</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {mensajes.map((mensaje) => (
              <div
                key={mensaje.id}
                className={cn(
                  "flex",
                  mensaje.rol === 'user' ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[85%] rounded-lg px-4 py-2",
                    mensaje.rol === 'user'
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{mensaje.contenido}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {new Date(mensaje.created_at).toLocaleTimeString('es-ES', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            ))}
            {enviando && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
            )}
            <div ref={mensajesEndReference} />
          </div>
        )}
      </ScrollArea>
      
      <form onSubmit={onEnviar} className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            ref={inputReference}
            value={inputMensaje}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder="Escribe tu pregunta..."
            disabled={enviando}
            className="flex-1"
            maxLength={2000}
          />
          <Button
            type="submit"
            size="icon"
            disabled={enviando || !inputMensaje.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </>
  )
}
