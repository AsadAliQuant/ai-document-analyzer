import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import * as api from '../api/client'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()

  useEffect(()=>{
    (async () => {
      const t = api.getTokens()
      if (!t?.access_token) return
      try {
        const m = await api.me()
        if (m.role === 'admin') navigate('/panel', { replace: true })
      } catch (_) {}
    })()
  }, [])

  async function onSubmit(e){
    e.preventDefault()
    setError('')
    setLoading(true)
    try{
      const tokens = await api.login(email.trim(), password)
      if (tokens?.user?.role === 'admin') {
        navigate('/panel', { replace: true })
      } else {
        setError('Not an admin account')
      }
    } catch (err){
      setError(err?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative text-foreground">
      <div className="absolute inset-0 bg-[url('/login-side.jpg')] bg-cover bg-center" />
      <div className="absolute inset-0 bg-black/20" />
      <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-sm rounded-xl border shadow-lg bg-white dark:bg-neutral-900 p-6 sm:p-8">
          <div className="mb-6">
            <div className="text-xl font-bold">AI App Console</div>
          </div>
          <div className="mb-6">
            <div className="text-2xl md:text-3xl font-bold">Welcome Back!</div>
          </div>
          <form onSubmit={onSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm">Email</Label>
              <Input id="email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required className="h-12 border-0 border-b rounded-none px-0 focus-visible:ring-0 focus-visible:border-foreground" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e=>setPassword(e.target.value)}
                  required
                  className="h-12 border-0 border-b rounded-none pr-10 pl-0 focus-visible:ring-0 focus-visible:border-foreground"
                />
                <button
                  type="button"
                  onClick={()=>setShowPassword(v => !v)}
                  className="absolute inset-y-0 right-0 flex items-center justify-center px-2 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.75 12c1.227 4.338 5.24 7.5 9.75 7.5 1.563 0 3.046-.355 4.388-.987M6.228 6.228A10.45 10.45 0 0111.5 4.5c4.51 0 8.523 3.162 9.75 7.5a10.523 10.523 0 01-4.199 5.421M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12s3.75-6.75 9.25-6.75S20.75 12 20.75 12s-3.75 6.75-9.25 6.75S2.25 12 2.25 12z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            {error && <div className="text-sm text-muted-foreground">{error}</div>}
            <Button type="submit" disabled={loading} className="w-full h-10 text-[15px]">
              {loading ? 'Logging in...' : 'Login Now'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
