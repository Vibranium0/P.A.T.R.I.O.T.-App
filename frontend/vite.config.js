import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5001',
    },
  },

  optimizeDeps: {
    include: ['framer-motion', 'react'],
  },

  build: {
    chunkSizeWarningLimit: 800,
  },
});
