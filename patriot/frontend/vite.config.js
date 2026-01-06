import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      'shared': path.resolve(__dirname, '../../shared'),
      'sentinel_login': path.resolve(__dirname, '../../sentinel_login'),
      'react-icons': path.resolve(__dirname, './node_modules/react-icons'),
    },
  },

  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5001',
    },
  },

  optimizeDeps: {
    include: ['framer-motion', 'react', 'react-icons/fi'],
  },

  build: {
    chunkSizeWarningLimit: 800,
  },
});
