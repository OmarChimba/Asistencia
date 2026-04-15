import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-oxc'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const host        = env.VITE_HOST         || 'localhost'
  const port        = parseInt(env.VITE_PORT)        || 5173
  const backendPort = parseInt(env.VITE_BACKEND_PORT) || 8000

  return {
    plugins: [react()],
    server: {
      host,
      port,
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      },
    },
  }
})
