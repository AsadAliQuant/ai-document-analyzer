import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../api/client'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Select } from '../components/ui/select'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Table, THead, TBody, TR, TH, TD } from '../components/ui/table'
import { Dialog } from '../components/ui/dialog'
import { useToast } from '../components/toast/ToastProvider.jsx'

function rndPass(len = 12){
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*'
  let s=''; for(let i=0;i<len;i++){ s += chars[Math.floor(Math.random()*chars.length)] }
  return s
}

export default function Dashboard(){
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [me, setMe] = useState(null)
  const [users, setUsers] = useState([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [cForm, setCForm] = useState({ firstName:'', lastName:'', email:'', password:'', role:'user', status:'active' })
  const [pwModalOpen, setPwModalOpen] = useState(false)
  const [pwUser, setPwUser] = useState(null)
  const [pwValue, setPwValue] = useState('')
  const [q, setQ] = useState('')
  const [nameSort, setNameSort] = useState('asc')

  useEffect(()=>{ (async ()=>{
    try{
      const m = await api.me()
      if (m.role !== 'admin') throw new Error('not admin')
      setMe(m)
      await loadUsers()
    } catch(e){
      navigate('/login', { replace:true })
    }
  })() },[])

  async function loadUsers(){
    setLoadingUsers(true)
    try{
      const data = await api.listUsers()
      setUsers(data.users || [])
    } finally { setLoadingUsers(false) }
  }

  async function onCreateUser(e){
    e.preventDefault()
    try{
      const name = `${cForm.firstName} ${cForm.lastName}`.trim() || null
      await api.createUser({
        name,
        email: cForm.email,
        password: cForm.password,
        role: cForm.role,
        status: cForm.status,
      })
      addToast({ title: 'User created', variant: 'success' })
      setCForm({ firstName:'', lastName:'', email:'', password:'', role:'user', status:'active' })
      await loadUsers()
    } catch (err){
      addToast({ title: 'Create failed', description: err?.message || 'Failed', variant: 'error' })
    }
  }

  async function onResetPassword(id){
    const newpw = rndPass()
    try{
      await api.resetPassword(id, newpw)
      addToast({ title: 'Password reset', description: 'New password: ' + newpw, variant: 'success', duration: 6000 })
    } catch(e){
      addToast({ title: 'Reset failed', variant: 'error' })
    }
  }

  async function onToggleStatus(id, next){
    try{ await api.updateStatus(id, next); await loadUsers(); addToast({ title: 'Status updated', variant: 'success' }) } catch(e){ addToast({ title: 'Update failed', variant: 'error' }) }
  }

  function openSetPassword(user){
    setPwUser(user)
    setPwValue('')
    setPwModalOpen(true)
  }

  async function saveCustomPassword(){
    if (!pwUser?.id || !pwValue) return
    try{
      await api.resetPassword(pwUser.id, pwValue)
      setPwModalOpen(false)
      addToast({ title: 'Password updated', variant: 'success' })
    } catch(e){
      addToast({ title: 'Update failed', description: e?.message, variant: 'error' })
    }
  }

  async function onDeleteUser(user){
    if (!user?.id) return
    const ok = window.confirm(`Delete user ${user.email}?`)
    if (!ok) return
    try{
      await api.deleteUser(user.id)
      addToast({ title: 'User deleted', variant: 'success' })
      await loadUsers()
    } catch(e){
      addToast({ title: 'Delete failed', description: e?.message, variant: 'error' })
    }
  }

  async function onLogout(){
    await api.logoutAll()
    navigate('/login', { replace:true })
  }

  const visibleUsers = (users || [])
    .filter(u => (u.role !== 'admin'))
    .filter(u => {
      const s = q.trim().toLowerCase()
      if (!s) return true
      const name = (u.name || '').toLowerCase()
      const email = (u.email || '').toLowerCase()
      return name.includes(s) || email.includes(s)
    })
    .sort((a,b) => {
      const an = (a.name || '').toLowerCase()
      const bn = (b.name || '').toLowerCase()
      const cmp = an.localeCompare(bn)
      return nameSort === 'desc' ? -cmp : cmp
    })

  return (
    <div className="min-h-screen p-6 bg-background text-foreground">
      <header className="flex items-center justify-between rounded-xl bg-black px-6 py-5 text-white shadow-lg">
        <h2 className="text-2xl font-semibold">AI Analyzer App - Admin Panel</h2>
        <div className="flex items-center gap-4">
          <span className="text-sm text-white/70">{me ? `${me.email} (${me.role})` : ''}</span>
          <Button
            variant="outline"
            onClick={onLogout}
            className="bg-white text-black border-transparent hover:bg-white/90"
          >
            Logout
          </Button>
        </div>
      </header>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Create User</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={onCreateUser} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="c_first">First Name</Label>
                  <Input id="c_first" value={cForm.firstName} onChange={e=>setCForm(f=>({...f, firstName:e.target.value}))} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="c_last">Last Name</Label>
                  <Input id="c_last" value={cForm.lastName} onChange={e=>setCForm(f=>({...f, lastName:e.target.value}))} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="c_email">Email</Label>
                <Input id="c_email" type="email" required value={cForm.email} onChange={e=>setCForm(f=>({...f, email:e.target.value}))} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="c_password">Password</Label>
                <Input id="c_password" required value={cForm.password} onChange={e=>setCForm(f=>({...f, password:e.target.value}))} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="c_role">Role</Label>
                  <Select id="c_role" value={cForm.role} onChange={e=>setCForm(f=>({...f, role:e.target.value}))}>
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="c_status">Status</Label>
                  <Select id="c_status" value={cForm.status} onChange={e=>setCForm(f=>({...f, status:e.target.value}))}>
                    <option value="active">active</option>
                    <option value="disabled">disabled</option>
                  </Select>
                </div>
              </div>
              <div className="flex items-center justify-end">
                <Button type="submit">Create</Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row md:items-center gap-3 mb-2">
              <div className="flex-1">
                <Input placeholder="Search name or email" value={q} onChange={e=>setQ(e.target.value)} />
              </div>
              <div className="w-full md:w-40">
                <Select value={nameSort} onChange={e=>setNameSort(e.target.value)}>
                  <option value="asc">Name A→Z</option>
                  <option value="desc">Name Z→A</option>
                </Select>
              </div>
            </div>
            <div className="text-sm text-muted-foreground mb-2">Reset password sets a new random password and shows it once.</div>
            <div className="overflow-x-auto">
              <Table>
                <THead>
                  <TR>
                    <TH>ID</TH>
                    <TH>Email</TH>
                    <TH>Name</TH>
                    <TH>Role</TH>
                    <TH>Status</TH>
                    <TH>Actions</TH>
                  </TR>
                </THead>
                <TBody>
                  {loadingUsers ? (
                    <TR><TD colSpan={6}>Loading...</TD></TR>
                  ) : visibleUsers.length === 0 ? (
                    <TR><TD colSpan={6}>No users</TD></TR>
                  ) : visibleUsers.map(u => (
                    <TR key={u.id}>
                      <TD>{u.id}</TD>
                      <TD>{u.email}</TD>
                      <TD>{u.name || ''}</TD>
                      <TD>{u.role}</TD>
                      <TD>{u.status}</TD>
                      <TD className="space-x-2">
                        <Button variant="outline" size="sm" onClick={()=>onResetPassword(u.id)}>Reset PW</Button>
                        <Button variant="outline" size="sm" onClick={()=>openSetPassword(u)}>Set PW</Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="bg-black text-white border-transparent hover:bg-black/85"
                          onClick={()=>onToggleStatus(u.id, u.status === 'active' ? 'disabled' : 'active')}
                        >
                          {u.status === 'active' ? 'Disable' : 'Activate'}
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          className="bg-red-600 text-white hover:bg-red-700 border-transparent"
                          onClick={()=>onDeleteUser(u)}
                        >
                          Delete
                        </Button>
                      </TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog
        open={pwModalOpen}
        onClose={()=>setPwModalOpen(false)}
        title={pwUser ? `Set Password: ${pwUser.email}` : 'Set Password'}
        footer={(
          <>
            <Button variant="outline" onClick={()=>setPwModalOpen(false)}>Cancel</Button>
            <Button onClick={saveCustomPassword} disabled={!pwValue}>Save</Button>
          </>
        )}
      >
        <div className="space-y-2">
          <Label htmlFor="pw_new">New Password</Label>
          <Input id="pw_new" value={pwValue} onChange={e=>setPwValue(e.target.value)} />
        </div>
      </Dialog>
    </div>
  )
}
