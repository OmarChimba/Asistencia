import { useState, useEffect } from 'react'
import { getMe } from './api'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

function Header() {
  return (
    <header className="app-header">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
      <div>
        <h1>Reporte de Asistencia</h1>
        <p>{new Date().toLocaleDateString('es-EC', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>
    </header>
  )
}

export default function App() {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  // Restaurar sesión desde token guardado
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setLoading(false); return }
    getMe()
      .then(setUser)
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  const handleLogin = (userData) => setUser(userData)

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  if (loading) {
    return (
      <>
        <Header />
        <div className="loading-overlay">
          <div className="spinner" />
          <span>Cargando...</span>
        </div>
      </>
    )
  }

  return (
    <>
      <Header />
      {user
        ? <Dashboard user={user} onLogout={handleLogout} />
        : <Login onLogin={handleLogin} />
      }
    </>
  )
}
