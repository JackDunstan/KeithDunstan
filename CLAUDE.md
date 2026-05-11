## Quick Reference

**Project:** Digital archive of Keith Dunstan (1925–2013), Australian journalist and author.  
**Site:** https://keithdunstan.org — built with Eleventy (11ty) + Bootstrap 5 (11straps boilerplate), Gulp, deployed via Netlify from GitHub.

**Content lives in:**
- `src/posts/[collection-slug]/` — all readable content (both book chapters and magazine articles)
- Book intro/index pages sit directly in `src/` (e.g. `src/supporting-a-column.md`, `src/batman-in-the-bulletin.njk`)

**Current collections under `src/posts/`:**
| Slug | Type | Description |
|------|------|-------------|
| `no-brains-at-all` | Book | Memoir, 1990 |
| `supporting-a-column` | Book | Memoir, 1966 |
| `a-day-in-the-life-of-australia` | Book | Bicentennial history, 1989 |
| `bulletin` | Articles | Written under pseudonym "John Batman" |
| `walkabout-magazine` | Articles | Walkabout magazine pieces |

**Default layout and `post` tag** are set globally by `src/posts/posts.json` — don't repeat them in frontmatter.

**Key constraints:**
- Do not manually edit `dev/`, `public/`, or `docs/` — all are build output
- Preserve Keith Dunstan's voice exactly; Australian English; single-quote dialogue
- Tags are granular proper nouns only (people, places, organisations)
- Article files should have 5–15 tags; book chapter files may have empty tags
- Every `.md` file requires `title`, `date`, and `summary` frontmatter
- Article files may also use a `categories` field (e.g. `- The Bulletin`)

**Frontmatter example — article:**
```yaml
---
title: Alas, poor Tivoli, I knew it well.
date: 1967-04-15
summary: First published in the Bulletin Magazine, 1967.
categories:
- The Bulletin
tags:
  - Tivoli theatre
  - Melbourne
---
```

**Frontmatter example — book chapter:**
```yaml
---
title: Introduction
date: 1990-11-11
summary: The opening for his first book of memoirs, 'No Brains At All'.
tags:
---
```

**Build:**
```bash
npm run watch    # local dev (output → dev/)
npm run build    # production build (output → public/, what Netlify deploys)
```

**Deploy:** `git push` to `master` triggers Netlify build automatically (configured in `netlify.toml`, publishes from `public/`).

**OCR tooling:** `ocr/` contains a Node.js OCR pipeline (`ocr/index.js`) using `node-tesseract-ocr` for processing scanned documents into markdown.
