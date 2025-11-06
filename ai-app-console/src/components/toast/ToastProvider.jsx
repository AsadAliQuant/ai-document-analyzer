import React, { createContext, useContext, useMemo, useState, useCallback } from 'react'

const ToastCtx = createContext(null)

let _id = 1

function ToastItem({ t, onClose }){
  const base = 'text-white shadow rounded-md px-4 py-3 mb-2 flex items-start gap-3 min-w-[260px]'
  const cls = t.variant === 'success'
    ? 'bg-green-600'
    : t.variant === 'warning'
    ? 'bg-yellow-600'
    : t.variant === 'error'
    ? 'bg-red-600'
    : 'bg-gray-800'
  return (
    <div className={`${base} ${cls}`} role="status">
      <div className="flex-1">
        {t.title && <div className="font-medium">{t.title}</div>}
        {t.description && <div className="text-sm opacity-90 break-words">{t.description}</div>}
      </div>
      <button className="opacity-80 hover:opacity-100" onClick={()=>onClose(t.id)} aria-label="Close">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
  )
}

export function ToastProvider({ children }){
  const [toasts, setToasts] = useState([])

  const remove = useCallback((id)=> setToasts(ts => ts.filter(t => t.id !== id)), [])

  const add = useCallback(({ title, description, variant = 'info', duration = 3500 }) => {
    const id = _id++
    const t = { id, title, description, variant }
    setToasts(ts => [...ts, t])
    if (duration > 0){
      setTimeout(() => remove(id), duration)
    }
    return id
  }, [remove])

  const value = useMemo(()=>({ addToast: add, removeToast: remove }), [add, remove])

  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-50">
        {toasts.map(t => (
          <ToastItem key={t.id} t={t} onClose={remove} />
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast(){
  const ctx = useContext(ToastCtx)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
