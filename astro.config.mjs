import { defineConfig } from 'astro/config';
import tailwind from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import path from 'path';

// https://astro.build/config
export default defineConfig({
  site: 'https://tripleoakservices.com',
  integrations: [sitemap()],
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
