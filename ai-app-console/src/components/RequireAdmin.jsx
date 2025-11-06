import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import * as api from '../api/client'

export default function RequireAdmin({ children }){
  const [checking, setChecking] = useState(true)
  const [ok, setOk] = useState(false)
  const navigate = useNavigate()
  const loc = useLocation()

  useEffect(()=>{
    let mounted = true
    ;(async () => {
      const tokens = api.getTokens()
      if (!tokens?.access_token) {
        navigate('/login', { replace: true, state: { from: loc.pathname } })
        return
      }
      try {
        const me = await api.me()
        if (mounted) {
          if (me.role === 'admin') { setOk(true) } else { navigate('/login', { replace: true }) }
        }
      } catch (_) {
        if (mounted) navigate('/login', { replace: true })
      } finally {
        if (mounted) setChecking(false)
      }
    })()
    return () => { mounted = false }
  }, [loc.pathname])

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        Checking access...
      </div>
    )
  }
  if (!ok) return null
  return children
}
