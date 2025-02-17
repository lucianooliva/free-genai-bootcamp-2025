import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: '5173'
  },
  define: {
    'process.env': {
      GROQ_API_KEY: process.env.VITE_GROQ_API_KEY
    }
  }
});
