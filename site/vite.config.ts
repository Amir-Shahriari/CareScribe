import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Served from https://amir-shahriari.github.io/CareScribe/ via GitHub Pages.
// https://vite.dev/config/
export default defineConfig({
  base: '/CareScribe/',
  plugins: [react(), tailwindcss()],
})
