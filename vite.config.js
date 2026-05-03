import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import localApiGateway from './vite-plugin-local-api.js'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Dev-only: Local API Gateway – exposes /api/* endpoints with live sensor state
    ...(process.env.NODE_ENV === 'development' ? [localApiGateway()] : [])
  ],
  assetsInclude: ['**/*.onnx'],
  base: process.env.NODE_ENV === 'production' ? '/IntentScope/' : '/',
  server: {
    port: 3000,
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
    },
  },
  // Worker support: using native new Worker(new URL(...)) syntax
  // No special plugin needed for basic worker imports
})
