import { useState } from 'react'
import { loginApi } from '../api'

export default function Login({ onLogin }) {
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!email || !password) { setError('Completa todos los campos.'); return }

    setLoading(true)
    try {
      const data = await loginApi(email.trim().toLowerCase(), password)
      localStorage.setItem('token', data.token)
      onLogin({ nombre: data.nombre, is_admin: data.is_admin, grupos: data.grupos })
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al conectar con el servidor.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#aa0fcd" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
        <h2>Iniciar Sesión</h2>
        <p className="subtitle">Ingresa tus credenciales para ver el reporte de tu grupo</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Correo electrónico</label>
            <div className="input-wrap">
              <span className="input-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
              </span>
              <input
                id="email" type="email" autoComplete="username"
                placeholder="usuario@nintanga.com.ec"
                value={email} onChange={e => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <div className="input-wrap">
              <span className="input-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </span>
              <input
                id="password" type="password" autoComplete="current-password"
                placeholder="***********"
                value={password} onChange={e => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && <div className="login-error">{error}</div>}

          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Verificando...' : 'Ingresar'}
          </button>
        </form>
      </div>
    </div>
  )
}
