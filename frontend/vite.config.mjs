import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'https://rocket-pitch-backend.onrender.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    // Make sure routes are handled correctly
    historyApiFallback: true
  },
  build: {
    // Generate sourcemaps for better debugging
    sourcemap: true
  }
})
