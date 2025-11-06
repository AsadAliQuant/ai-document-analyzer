import * as React from 'react'
import { cn } from '../../lib/utils'

const Table = ({ className, ...props }) => (
  <table className={cn('w-full caption-bottom text-sm', className)} {...props} />
)
const THead = ({ className, ...props }) => (
  <thead className={cn('[&_tr]:border-b', className)} {...props} />
)
const TBody = ({ className, ...props }) => (
  <tbody className={cn('[&_tr:last-child]:border-0', className)} {...props} />
)
const TR = ({ className, ...props }) => (
  <tr className={cn('border-b transition-colors hover:bg-muted/40', className)} {...props} />
)
const TH = ({ className, ...props }) => (
  <th className={cn('h-10 px-2 text-left align-middle font-medium text-foreground', className)} {...props} />
)
const TD = ({ className, ...props }) => (
  <td className={cn('p-2 align-middle', className)} {...props} />
)

export { Table, THead, TBody, TR, TH, TD }
