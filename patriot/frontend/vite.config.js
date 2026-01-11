import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../../shared'),
      'sentinel_login': path.resolve(__dirname, '../../sentinel_login'),
      'react-icons': path.resolve(__dirname, './node_modules/react-icons'),
    },
    dedupe: ['react', 'react-dom', 'classnames', '@heroicons/react'],
  },

  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
    },
    fs: {
      // Allow serving files from the shared directory and shared/ui/components
      allow: [
        '..',
        '../..',
        path.resolve(__dirname, '../../shared'),
        path.resolve(__dirname, '../../shared/ui/components'),
      ],
    },
  },

  optimizeDeps: {
    include: [
      'framer-motion',
      'react',
      'react-icons/fi',
      'classnames',
      '@heroicons/react',
      '@heroicons/react/24/outline',
    ],
    exclude: [],
  },

  build: {
    chunkSizeWarningLimit: 800,
  },
});
