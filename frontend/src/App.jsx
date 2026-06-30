import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { supabase } from './supabase'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import DatasetView from './pages/DatasetView'
import { LayoutDashboard, History as HistoryIcon, LogOut, ShieldAlert } from 'lucide-react'

// Custom Route Guard for Authentication
function ProtectedRoute({ children, session }) {
  if (!session) {
    return <Navigate to="/login" replace />
  }
  return children
}

// Global Navigation Bar
function Navbar({ session }) {
  const location = useLocation()
  
  const handleLogout = async () => {
    await supabase.auth.signOut()
  }

  if (!session) return null

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        AutoDataset
      </Link>
      <div className="nav-links">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </Link>
        <Link 
          to="/history" 
          className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}
        >
          <HistoryIcon size={18} />
          History Logs
        </Link>
        <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
          <LogOut size={14} />
          Logout
        </button>
      </div>
    </nav>
  )
}

export default function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 1. Get initial authentication session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    // 2. Listen for active session state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#090d16' }}>
        <div className="spinner" style={{ width: '40px', height: '40px' }}></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="app-container">
        <Navbar session={session} />
        <main className="page-content">
          <Routes>
            <Route 
              path="/login" 
              element={session ? <Navigate to="/" replace /> : <Login />} 
            />
            <Route 
              path="/" 
              element={
                <ProtectedRoute session={session}>
                  <Dashboard session={session} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <ProtectedRoute session={session}>
                  <History session={session} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dataset/:id" 
              element={
                <ProtectedRoute session={session}>
                  <DatasetView session={session} />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}
