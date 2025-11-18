import React, { useState, createContext, useContext, useCallback } from 'react'; // Added useCallback
import { X } from 'lucide-react';

// --- Type Definitions ---
type ToastType = 'info' | 'success' | 'error';

interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  toast: (message: string, type: ToastType) => void;
}

// --- Context and Provider ---
const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const toast = useCallback((message: string, type: ToastType) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      setToasts((current) => current.filter((t) => t.id !== id));
    }, 4000);
  }, []); // Use useCallback to stabilize the toast function

  const removeToast = (id: number) => {
    setToasts((current) => current.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {/* Toaster Component: Renders the toasts */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(({ id, message, type }) => {
          const colors = {
            info: 'bg-blue-600 border-blue-700',
            success: 'bg-green-600 border-green-700',
            error: 'bg-red-600 border-red-700',
          };
          return (
            <div
              key={id}
              className={`relative w-80 max-w-sm p-4 text-white rounded-lg shadow-lg border ${colors[type]} animate-in slide-in-from-top-4 duration-300`}
            >
              <p className="text-sm font-medium">{message}</p>
              <button
                onClick={() => removeToast(id)}
                className="absolute top-1 right-1 p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

// --- Custom Hook ---
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};