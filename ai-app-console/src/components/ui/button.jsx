import * as React from 'react'
import { cva } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50 disabled:pointer-events-none border',
  {
    variants: {
      variant: {
        default: 'bg-foreground text-background hover:opacity-90 border-transparent',
        outline: 'bg-transparent text-foreground hover:bg-muted border-border',
        ghost: 'bg-transparent text-foreground hover:bg-muted border-transparent',
        secondary: 'bg-secondary text-secondary-foreground hover:opacity-90 border-transparent',
        destructive: 'bg-destructive text-destructive-foreground hover:opacity-90 border-transparent',
      },
      size: {
        default: 'h-9 px-4 py-2 rounded-md',
        sm: 'h-8 px-3 rounded-md',
        lg: 'h-10 px-6 rounded-lg',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  }
)

const Button = React.forwardRef(({ className, variant, size, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
))
Button.displayName = 'Button'

export { Button, buttonVariants }
