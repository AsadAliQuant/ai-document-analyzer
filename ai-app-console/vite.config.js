import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to local Apache/XAMPP
      '/ai-auth-api': {
        target: 'http://localhost',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            const auth = req.headers['authorization']
            if (auth) proxyReq.setHeader('authorization', auth)
          })
        },
      },
    },
  },
})
