#!/usr/bin/env python3
"""Apply approved page title/description changes from the DayStar queue to a static (Astro) client site.

Usage (from anywhere):
  py -3 scripts/static-seo-apply.py --client 4714 --repo C:/Users/AustinHayes/Documents/Websites/triple-oak-services [--push] [--dry-run]
  py -3 scripts/static-seo-apply.py --changes changes.json --repo <repo> --dry-run     (offline test, no server)

What it does, per approved card:
  1. finds the exact old title and description text as a literal in the repo's src/ (exactly one place each, or it skips the card and says why)
  2. replaces them with the approved text
  3. builds the site and checks the built page really has the new title and description
  4. only if every card verified: commits (and pushes with --push), then marks the cards applied in the dashboard
Anything it cannot place safely is left "approved" and listed, so a person (or Claude in that repo) can do it by hand.
"""
import argparse, html, json, os, re, subprocess, sys, tempfile

SSH = 'daystar'
WP = 'cd /home/dsdaystardigitalco/htdocs/daystardigital.co && sudo -u dsdaystardigitalco wp eval-file'

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode:
        sys.exit('FAILED: %s\n%s%s' % (cmd, r.stdout[-1500:], r.stderr[-1500:]))
    return r

def remote_php(code):
    with tempfile.NamedTemporaryFile('w', suffix='.php', delete=False, encoding='utf-8') as f:
        f.write('<?php\n' + code); local = f.name
    try:
        run(['scp', '-q', local, SSH + ':/tmp/sseo.php'])
        out = run(['ssh', SSH, WP + ' /tmp/sseo.php; rm -f /tmp/sseo.php']).stdout
    finally:
        os.unlink(local)
    return out

def fetch_changes(cid):
    out = remote_php("global $wpdb; $o = []; foreach ($wpdb->get_results($wpdb->prepare(\"SELECT id, payload FROM \" . dsq_t() . \" WHERE client_id = %%d AND kind = 'page_tune' AND status = 'approved' ORDER BY id\", %d)) as $r) { $p = json_decode($r->payload, true); $o[] = ['id' => (int) $r->id, 'path' => $p['path'], 'before' => $p['before'], 'after' => $p['after']]; } echo '@@' . wp_json_encode($o) . '@@';" % cid)
    m = re.search(r'@@(.*)@@', out, re.S)
    return json.loads(m.group(1)) if m else []

def mark_done(ids, note):
    remote_php("global $wpdb; foreach ([%s] as $id) $wpdb->update(dsq_t(), ['status' => 'applied', 'applied_at' => current_time('mysql'), 'note' => %s], ['id' => $id]); echo 'marked';" % (','.join(map(str, ids)), json.dumps(note)))

def variants(text):
    """Ways the same text can be written inside source code."""
    t = html.unescape(text); seen = []
    for v in (t, t.replace('&', '&amp;'), t.replace("'", "\\'"), t.replace('"', '\\"'), t.replace('&', '&amp;').replace("'", "\\'")):
        if v not in seen: seen.append(v)
    return seen

def literal_sites(repo, text):
    """All (file, variant) where the text appears as a complete quoted string in src/."""
    hits = []
    for root, _, files in os.walk(os.path.join(repo, 'src')):
        for fn in files:
            if not fn.endswith(('.astro', '.json', '.ts', '.js', '.mjs', '.md', '.mdx')): continue
            p = os.path.join(root, fn); s = open(p, encoding='utf-8', errors='ignore').read()
            for v in variants(text):
                for q in ('"', "'", '`'):
                    n = s.count(q + v + q)
                    if n: hits.append((p, q + v + q, q, v, n))
    return hits

def place(repo, text):
    hits = literal_sites(repo, text)
    total = sum(h[4] for h in hits)
    if total == 1: return hits[0], None
    return None, ('not found as a plain quoted string (the page builds it from a template)' if total == 0 else 'appears %d times in the source, so I cannot tell which is the page title' % total)

def escape_for(new, q, original_has_amp):
    t = html.unescape(new)
    if original_has_amp: t = t.replace('&', '&amp;')
    return t.replace('\\', '\\\\').replace(q, '\\' + q) if q in ('"', "'") else t

def built_page(repo, path):
    for cand in (os.path.join(repo, 'dist', path.strip('/'), 'index.html'), os.path.join(repo, 'dist', path.strip('/') + '.html')):
        if os.path.exists(cand): return open(cand, encoding='utf-8', errors='ignore').read()
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--client', type=int); ap.add_argument('--repo', required=True); ap.add_argument('--changes')
    ap.add_argument('--push', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(); repo = os.path.abspath(a.repo)
    changes = json.load(open(a.changes, encoding='utf-8')) if a.changes else fetch_changes(a.client)
    if not changes: print('Nothing approved and waiting for this site.'); return
    if run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=repo).stdout.strip(): sys.exit('The repo has uncommitted changes. Commit or stash them first.')
    run(['git', 'pull', '--ff-only'], cwd=repo, check=False)
    done, skipped = [], []
    for c in changes:
        if c.get('kind') == 'patch':  # exact text patches for page content and links: each find must appear exactly once in the file
            why = None; texts = {}
            for pt in c.get('patches', []):
                f = os.path.normpath(os.path.join(repo, pt['file']))
                if not f.startswith(os.path.join(repo, 'src') + os.sep) or not os.path.isfile(f): why = 'file %s not found' % pt['file']; break
                s = texts.get(f) or open(f, encoding='utf-8').read()
                if s.count(pt['find']) != 1: why = '%s: the anchor text appears %d times' % (pt['file'], s.count(pt['find'])); break
                texts[f] = s.replace(pt['find'], pt['replace'], 1)
            if why: skipped.append((c, why)); continue
            for f, s in texts.items(): open(f, 'w', encoding='utf-8', newline='').write(s)
            done.append(c); continue
        edits = []; why = None
        for field in ('title', 'desc'):
            old, new = c['before'].get(field, ''), c['after'][field]
            if not old: why = 'the page has no %s to replace in the source' % field; break
            hit, err = place(repo, old)
            if err: why = '%s: %s' % (field, err); break
            edits.append((field, hit, new))
        if why: skipped.append((c, why)); continue
        for field, hit, new in edits:
            f, lit, q, v, n = hit
            s = open(f, encoding='utf-8').read()
            s = s.replace(lit, q + escape_for(new, q, '&amp;' in v) + q, 1)
            open(f, 'w', encoding='utf-8', newline='').write(s)
        done.append(c)
    if done:
        print('Building...'); b = run('npm run build', cwd=repo, check=False)
        if b.returncode:
            run(['git', 'checkout', '--', 'src'], cwd=repo); sys.exit('Build failed, nothing changed.\n' + b.stdout[-1200:] + b.stderr[-1200:])
        bad = []
        for c in done:
            if c.get('kind') == 'patch':
                for ex in c.get('expects', []):
                    pg = built_page(repo, ex['path'])
                    if pg is None or html.unescape(ex['text']) not in html.unescape(pg): bad.append(c); break
                continue
            pg = built_page(repo, c['path'])
            t, d = html.unescape(c['after']['title']), html.unescape(c['after']['desc'])
            if pg is None or html.unescape(pg).count(t) < 1 or html.unescape(pg).count(d) < 1: bad.append(c)
        if bad:
            run(['git', 'checkout', '--', 'src'], cwd=repo)
            sys.exit('The built page did not show the new text for: ' + ', '.join(c['path'] for c in bad) + '. Nothing was kept.')
        print('Verified in the built site: ' + ', '.join(c['path'] for c in done))
        if a.dry_run:
            run(['git', 'checkout', '--', 'src'], cwd=repo); print('Dry run: changes reverted.')
        else:
            run(['git', 'add', 'src'], cwd=repo)
            run(['git', 'commit', '-q', '-m', 'SEO: approved titles and descriptions for ' + ', '.join(c['path'] for c in done) + '\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>'], cwd=repo)
            sha = run(['git', 'rev-parse', '--short', 'HEAD'], cwd=repo).stdout.strip()
            if a.push:
                run(['git', 'push', '-q'], cwd=repo)
                if not a.changes: mark_done([c['id'] for c in done], 'Written to the site repo (%s). Live when Cloudflare finishes building.' % sha)
                print('Pushed %s.' % sha)
            else:
                print('Committed %s locally. Re-run with --push (or push by hand) to go live; cards stay "approved" until then.' % sha)
    for c, why in skipped: print('LEFT FOR A PERSON: %s (card %s): %s' % (c['path'], c.get('id', '?'), why))
    if skipped: sys.exit(3)  # lets the publish job report that something could not be placed

if __name__ == '__main__': main()
