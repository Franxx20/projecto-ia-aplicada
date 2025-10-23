/**
 * Componente Toaster para renderizar notificaciones toast
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 */

'use client';

import { useToast } from '@/hooks/use-toast';

export function Toaster() {
  const { toasts } = useToast();

  return (
    <div className="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
      {toasts.map((toast) => {
        const { id, title, description, type = 'info' } = toast;
        
        const bgColors = {
          success: 'bg-green-50 border-green-200',
          error: 'bg-red-50 border-red-200',
          warning: 'bg-yellow-50 border-yellow-200',
          info: 'bg-blue-50 border-blue-200',
        };

        const textColors = {
          success: 'text-green-800',
          error: 'text-red-800',
          warning: 'text-yellow-800',
          info: 'text-blue-800',
        };

        return (
          <div
            key={id}
            className={`pointer-events-auto mb-2 w-full overflow-hidden rounded-lg border ${bgColors[type]} p-4 shadow-lg transition-all data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[state=closed]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:animate-in data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full`}
          >
            {title && (
              <div className={`text-sm font-semibold ${textColors[type]}`}>
                {title}
              </div>
            )}
            {description && (
              <div className={`mt-1 text-sm ${textColors[type]} opacity-90`}>
                {description}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
