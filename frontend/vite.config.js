import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? '/static/spa/' : '/',
  plugins: [vue()],
  build: {
    outDir: '../static/spa',
    emptyOutDir: true,
    assetsDir: '',
    rollupOptions: {
      output: {
        entryFileNames: 'main.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'style.css') {
            return 'main.css'
          }
          return '[name][extname]'
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
}))
