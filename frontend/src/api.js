import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Adjunta el token JWT en cada petición
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Si el token expiró o es inválido, limpia sesión y recarga
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.reload()
    }
    return Promise.reject(err)
  }
)

export const loginApi = (email, password) =>
  api.post('/login', { email, password }).then(r => r.data)

export const getMe = () =>
  api.get('/me').then(r => r.data)

export const getAsistencia = () =>
  api.get('/asistencia').then(r => r.data)

export default api
