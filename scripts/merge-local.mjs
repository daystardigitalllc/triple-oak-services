// Merges the per-city content files in src/data/local/*.json into the
// `local` object of each matching entry in src/data/locations.json.
// Franklin already has a hand-written `local` object, so its file only
// adds `sections` without overwriting the existing fields.
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const locPath = path.join(root, 'src', 'data', 'locations.json');
const dir = path.join(root, 'src', 'data', 'local');

const locations = JSON.parse(readFileSync(locPath, 'utf8'));

for (const file of readdirSync(dir).filter((f) => f.endsWith('.json'))) {
  const slug = file.replace('.json', '');
  const loc = locations.find((l) => l.slug === slug);
  if (!loc) { console.warn('No location for', file); continue; }
  const incoming = JSON.parse(readFileSync(path.join(dir, file), 'utf8'));
  loc.local = loc.local ? { ...loc.local, ...incoming } : incoming;
  console.log('merged', slug);
}

writeFileSync(locPath, JSON.stringify(locations, null, 2) + '\n');
