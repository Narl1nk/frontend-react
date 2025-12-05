import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Set the server port
    proxy: {
      '/api': {
        target: 'http://localhost:3000', // Proxy API requests
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist', // Output directory for the build
    sourcemap: true // Generate source map
  },
  resolve: {
    alias: {
      '@': '/src' // Path alias for src
    }
  }
});