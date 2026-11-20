// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => ({
  plugins: [react()], // Habilita el plugin de React para Vite
  server: {
    host: '0.0.0.0', // Permite que el servidor sea accesible desde otras IPs en la red
    port: 5173 // Define el puerto en el que se ejecutará la aplicación
  },
  esbuild: {
      drop: mode === 'production' ? ['console', 'debugger'] : [],
    },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('/node_modules/')) return;

          if (/\/node_modules\/(react|react-dom|react-router-dom|@remix-run\/router)\//.test(id)) {
            return 'react-vendor';
          }

          if (/\/node_modules\/(chart\.js|moment|chartjs-adapter-moment)\//.test(id)) {
            return 'chart-vendor';
          }
        },
      },
    },
  },
}));
