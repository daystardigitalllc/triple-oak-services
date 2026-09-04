import { defineConfig } from 'astro/config';
import tailwind from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import path from 'path';

// https://astro.build/config
// Site is fully static. The /api/quote endpoint (Resend email sending)
// is NOT an Astro route - it's a Cloudflare Pages Function at
// functions/api/quote.js, which Cloudflare's existing Pages git-deploy
// pipeline picks up automatically alongside the static build, no
// adapter or output-mode change needed here.
export default defineConfig({
  site: 'https://tripleoakservices.com',
  integrations: [sitemap()],
  vite: {
    plugins: [tailwind()],
    resolve: {
      alias: {
        '@': path.resolve('./src')
      }
    }
  },
});
