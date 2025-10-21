/**
 * Hook para mostrar notificaciones toast
 * Basado en el patrón de shadcn/ui
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 */

import { useState, useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  type?: ToastType;
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
}

let toastCount = 0;
const listeners: Array<(state: ToastState) => void> = [];
let memoryState: ToastState = { toasts: [] };

function dispatch(action: { type: string; toast?: Toast; toastId?: string }) {
  if (action.type === 'ADD_TOAST') {
    memoryState = {
      toasts: [...memoryState.toasts, action.toast!],
    };
  } else if (action.type === 'REMOVE_TOAST') {
    memoryState = {
      toasts: memoryState.toasts.filter((t) => t.id !== action.toastId),
    };
  } else if (action.type === 'DISMISS_TOAST') {
    memoryState = {
      toasts: memoryState.toasts.map((t) =>
        t.id === action.toastId ? { ...t, open: false } : t
      ),
    };
  }
  
  listeners.forEach((listener) => {
    listener(memoryState);
  });
}

function genId() {
  toastCount = (toastCount + 1) % Number.MAX_VALUE;
  return toastCount.toString();
}

export function toast(props: Omit<Toast, 'id'>) {
  const id = genId();
  
  const newToast: Toast = {
    ...props,
    id,
    duration: props.duration ?? 3000,
  };

  dispatch({
    type: 'ADD_TOAST',
    toast: newToast,
  });

  // Auto-dismiss after duration
  if (newToast.duration && newToast.duration > 0) {
    setTimeout(() => {
      dispatch({
        type: 'REMOVE_TOAST',
        toastId: id,
      });
    }, newToast.duration);
  }

  return {
    id,
    dismiss: () => dispatch({ type: 'REMOVE_TOAST', toastId: id }),
  };
}

export function useToast() {
  const [state, setState] = useState<ToastState>(memoryState);

  useEffect(() => {
    listeners.push(setState);
    return () => {
      const index = listeners.indexOf(setState);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }, []);

  return {
    toasts: state.toasts,
    toast,
    dismiss: (toastId: string) => dispatch({ type: 'REMOVE_TOAST', toastId }),
  };
}
