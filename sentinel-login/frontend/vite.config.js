import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            shared: resolve(__dirname, '../../shared'),
        },
        dedupe: ['react', 'react-dom', 'classnames'],
    },
    server: {
        port: 5173,
        open: true,
    },
    optimizeDeps: {
        include: ['classnames'],
    },
});
