import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), ''); // Load all env variables

  return {
    plugins: [react()],
    define: {
      'process.env': env, // Make all loaded env variables available under process.env
      // Or specifically define individual variables:
      // 'process.env.VITE_SOME_VAR': JSON.stringify(env.VITE_SOME_VAR),
    },
  };
});