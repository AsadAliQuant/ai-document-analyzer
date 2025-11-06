import * as React from 'react'
import { cn } from '../../lib/utils'

export function Dialog({ open, onClose, title, children, footer }){
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className={cn('relative z-10 w-full max-w-md rounded-lg border bg-card text-card-foreground shadow-lg')}> 
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
        <div className="p-4">
          {children}
        </div>
        {footer && (
          <div className="p-4 border-t flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
