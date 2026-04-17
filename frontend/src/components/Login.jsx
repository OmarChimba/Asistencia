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
      onLogin({ nombre: data.nombre, is_admin: data.is_admin, grupos: data.grupos, grupoLabels: data.grupoLabels })
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al conectar con el servidor.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <img src="/LogoNintanga.png" alt="Nintanga" className="login-logo" />
        <h2>Iniciar Sesión</h2>
        <p className="subtitle">Ingresa tus credenciales para ver el reporte de tu grupo</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Correo electrónico</label>
            <div className="input-wrap">
              <span className="input-icon"><i className="bx bx-envelope" /></span>
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
              <span className="input-icon"><i className="bx bx-lock-alt" /></span>
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
