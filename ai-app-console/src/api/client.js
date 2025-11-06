const STORAGE_KEY = 'tokens'
const API = '/ai-auth-api/'

export function getTokens(){
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') } catch { return null }
}
export function setTokens(t){ localStorage.setItem(STORAGE_KEY, JSON.stringify(t)) }
export function clearTokens(){ localStorage.removeItem(STORAGE_KEY) }

async function readError(res){
  try { const t = await res.json(); return t?.error || res.statusText || 'Request failed' } catch { return res.statusText || 'Request failed' }
}

async function refreshIfNeeded(tokens){
  if (!tokens?.refresh_token) return null
  const res = await fetch(API + 'token/refresh', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: tokens.refresh_token })
  })
  if (!res.ok) return null
  const data = await res.json()
  setTokens(data)
  return data
}

export async function authFetch(path, options = {}){
  const opts = { ...options, headers: { ...(options.headers || {}) } }
  let tokens = getTokens()
  if (tokens?.access_token) { opts.headers['Authorization'] = 'Bearer ' + tokens.access_token }
  const attempt = () => fetch(API + path, opts)
  let res = await attempt()
  if (res.status === 401 && tokens?.refresh_token){
    const newTokens = await refreshIfNeeded(tokens)
    if (newTokens){
      opts.headers['Authorization'] = 'Bearer ' + newTokens.access_token
      res = await attempt()
    }
  }
  return res
}

export async function login(email, password){
  const res = await fetch(API + 'login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!res.ok){ throw new Error(await readError(res)) }
  const tokens = await res.json()
  setTokens(tokens)
  return tokens
}

export async function logoutAll(){
  await authFetch('logout', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ all: true })
  })
  clearTokens()
}

export async function me(){
  const res = await authFetch('me', { method: 'GET' })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function listUsers(){
  const res = await authFetch('admin/users', { method: 'GET' })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function createUser(payload){
  const res = await authFetch('admin/users', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function resetPassword(id, new_password){
  const res = await authFetch(`admin/users/${id}/reset-password`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_password })
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function updateStatus(id, status){
  const res = await authFetch(`admin/users/${id}/status`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function deleteUser(id){
  // Try DELETE first
  let res = await authFetch(`admin/users/${id}`, { method: 'DELETE' })
  if (res.status === 405 || res.status === 404) {
    // Fallback to POST /delete for environments that block DELETE
    res = await authFetch(`admin/users/${id}/delete`, { method: 'POST' })
  }
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}
