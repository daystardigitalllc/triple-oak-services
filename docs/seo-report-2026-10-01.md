# Triple Oak Services SEO report, 2026-10-01

Scope: repo `daystardigitalllc/triple-oak-services` (Astro static site on Cloudflare Pages) plus read-only checks of the live site. No GSC or Google Business Profile access was available in this session, so the GSC figures in the brief (472 impressions / 10 clicks, Franklin around position 70) are **not re-verified here**. No outreach, form submissions or listing creation were done.

## 1. Applied

| Change | File | Evidence | Rollback |
|---|---|---|---|
| Removed `socials.google` (`https://g.page/triple-oak-services`) | `src/data/business.json` | The URL returns 302 to a plain `google.com/search?q=triple-oak-services` page, not a Business Profile. It fed the footer "Google Business" icon and the `sameAs` array in the LocalBusiness JSON-LD on every page. | `git revert` the commit. Restore the real GBP URL once verified. |

`npx astro build` completes (89 pages). Live HTTP checks are not possible for this change until it is deployed.

## 2. Verified live (no change needed)

- `http://` redirects 301 to `https://` non-www.
- Pages without a trailing slash redirect 308 to the trailing-slash URL. Canonicals (`/locations/franklin/`) and sitemap `<loc>` values use the trailing slash, so they are consistent.
- `https://www.tripleoakservices.com/` returns **200** (no redirect). Its canonical points to the non-www URL, so there is no duplicate-content risk today, but a 301 would consolidate link signals.
- Sitemap index and `sitemap-0.xml` are live and include the home page, `/locations/`, all 13 city hubs and all 65 city-by-service pages.
- `robots.txt` allows all and references the sitemap.

## 3. Audit: city-by-service page similarity

Method: built `dist/`, extracted `<main>` text of the 65 `/locations/<city>/<service>/` pages, compared 5-word shingles (Jaccard).

- Median page length is about 357 words.
- The same service across different cities shares on average **44-48%** of its shingles (max 54-57%). Part of that is shared boilerplate (FAQ, reviews, "What's Included"), but the only city-specific text is two sentences (`character` and `angle` from `locations.json`).
- Different services in Franklin overlap about 13-18%, so the pages are distinct by service.
- Recommendation: **do not add more city pages and do not delete any** until the existing pages carry real city-specific facts. Franklin is the only location worth enriching first. Thin, near-duplicate pages are the more likely cause of the weak Franklin rankings than missing pages, but that is a hypothesis; the GSC query/page data is needed to confirm.

## 4. Drafts awaiting owner facts (Franklin)

The repo holds no documented Franklin projects, crew, equipment or service boundaries, so nothing was written for these. Needed from the owner:

1. 2-4 real Franklin-area jobs: neighborhood or street area (the owner's choice of how specific), service, date, what made it hard (access, structure, lines), and permission to use the photos.
2. Debris handling: chipped on site, hauled, or logs left; disposal practice.
3. Crew and equipment actually used (bucket truck, crane, grinder size, trailer) and typical crew size.
4. Real service boundaries: which parts of Williamson County are served, any distance limits, and storm-response availability for Franklin.
5. Historic-district or HOA/permit experience in Franklin. Only state what was really done.
6. Whether the company has any ISA or TCIA credential. Until evidence is supplied, make no such claim. The site currently claims only "Licensed & Insured", "Free Estimates" and "Locally Owned".

Suggested Franklin changes once facts exist (all on existing URLs):
- `/locations/franklin/`: add a "Recent Franklin work" section and a service-area paragraph; keep the H1 `Tree Service in Franklin, TN`.
- `/locations/franklin/tree-removal/` and `/storm-damage-cleanup/` first, since those are the queries near position 70. Replace the generic paragraph with one real job write-up, debris and equipment detail.
- Add links from the home page and `/services/tree-removal` to the Franklin pages with a descriptive `<a href>`.

## 5. Other findings for the owner

- **Reviews and `aggregateRating`**: `MainLayout.astro` emits AggregateRating and Review JSON-LD from six reviews in `content.json`. Confirm they are genuine reviews from a platform the business controls, and note that Google may ignore review markup on a business's own pages for LocalBusiness ("self-serving reviews").
- **Copy**: the trimming copy says "proper arborist technique". It does not claim a certification, but consider "careful pruning technique" unless an arborist is on staff.
- **Facebook/Instagram links** (`facebook.com/triple-oak-services`, `instagram.com/triple-oak-services`) redirect to login walls; their existence could not be verified. Confirm they are real or remove them.
- **Address**: only city and state (Nashville, TN) are published, which suits a service-area business. Do not add a street address unless the business has a staffed location.
- **www redirect**: Cloudflare Pages `_redirects` cannot match hosts. Add a Bulk Redirect or Redirect Rule (www to apex, 301, preserve path) in the Cloudflare dashboard, then confirm with `curl -I https://www.tripleoakservices.com/`. Rollback: disable the rule. This is blocked pending dashboard access.

## 6. Citations and backlinks (all NOT CHECKED)

No listing was verified or created. Record, for each: live URL, status, NAP match, website link, date checked, evidence URL.

| Source | Status | Note |
|---|---|---|
| Google Business Profile | NOT CHECKED | The g.page link above was not valid. Confirm whether a profile exists and whether the business qualifies as a service-area business. |
| Bing Places, Apple Business Connect, Yelp, Facebook, BBB, local Chamber, Nextdoor, Yellow Pages, Foursquare, MapQuest, Manta, Local.com, EZlocal, Hotfrog | NOT CHECKED | Search for an existing listing first. A mention without a hyperlink is not a backlink. |
| Brownbook, Storeboard, ProvenExpert | NOT CHECKED, low priority | Check current terms. |
| Property managers, arborists, nurseries | NOT CHECKED | Outreach needs separate approval. |
| ISA/TCIA or other industry directories | NOT CHECKED | May carry fees and membership requirements; verify first. |

NAP to use: **Triple Oak Services**, 615-561-0472, https://tripleoakservices.com, service area per `business.json` (Nashville plus 12 listed cities), no street address.

## 7. Next three actions

1. Owner supplies the Franklin facts and photos in section 4; then enrich the Franklin hub and the tree-removal and storm-cleanup pages.
2. Pull GSC (Franklin queries and pages, 28/56/84 days against comparable periods, branded split from non-branded) and confirm the current positions.
3. Add the Cloudflare www-to-apex 301 and verify the real Google Business Profile, then audit the core citation list above.
