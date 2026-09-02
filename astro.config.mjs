import { defineConfig } from 'astro/config';
import tailwind from '@tailwindcss/vite';
import path from 'path';

// https://astro.build/config
export default defineConfig({
  vite: {
    plugins: [tailwind()],
    resolve: {
      alias: {
        '@': path.resolve('./src'),
        'astro:assets': path.resolve('./src/lib/astro-assets-mock.ts')
      }
    }
  },
});
