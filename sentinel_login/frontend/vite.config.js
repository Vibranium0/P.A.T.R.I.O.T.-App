import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';


export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            shared: resolve(__dirname, '../../shared'),
            '/shared': resolve(__dirname, '../../shared'),
            'react-icons': resolve(__dirname, './node_modules/react-icons'),
        },
        dedupe: ['react', 'react-dom', 'classnames'],
    },
    server: {
        port: 5175,
        open: true,
        fs: {
            allow: [
                resolve(__dirname, '../../shared'),
                resolve(__dirname, '.'),
            ],
        },
        proxy: {
            '/auth': 'http://localhost:5001'
        }
    },
    optimizeDeps: {
        include: ['classnames', 'react-icons/fi'],
    },
});
