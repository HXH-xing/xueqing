import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    allowedHosts: ['.trycloudflare.com'],
    proxy: {
      // 本地开发时把 /api 转发到后端,与生产同源行为一致
      '/api': 'http://127.0.0.1:8001'
    }
  },
  preview: {
    port: 5173,
    host: true,
    allowedHosts: ['.trycloudflare.com']
  }
})
