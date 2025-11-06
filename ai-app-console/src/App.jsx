import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import RequireAdmin from './components/RequireAdmin.jsx'

export default function App(){
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/panel" element={<RequireAdmin><Dashboard /></RequireAdmin>} />
      <Route path="/" element={<Navigate to="/panel" replace />} />
      <Route path="*" element={<Navigate to="/panel" replace />} />
    </Routes>
  )
}
