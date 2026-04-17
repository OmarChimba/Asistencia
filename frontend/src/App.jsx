import { useState, useEffect } from 'react'
import { getMe } from './api'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

function Header() {
  return (
    <header className="app-header">
      <img src="/LogoNintanga.png" alt="Nintanga" className="header-logo" />
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
