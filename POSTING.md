# Publishing a post

A post is one markdown file in `content/posts/`. Add the file, run the build,
commit, push. GitHub Pages redeploys in about a minute.

## The file

Name it `YYYY-MM-DD-some-slug.md`. The date in the filename is for sorting in a
file listing; the date that appears on the site comes from the front matter.

```markdown
---
title: What the 2026 rate case means for pumping costs
date: 2026-09-15
---

Opening paragraph. Blank lines separate paragraphs.

## A section heading

Body text. Use **bold** and *italic* sparingly, and [links](https://example.com)
where they help.

### A subheading

- A bullet
- Another bullet

Closing paragraph.
```

**Front matter fields**

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Appears as the page heading and in the browser tab |
| `date` | yes | `YYYY-MM-DD`. Sets the displayed date and the sort order |
| `slug` | no | Overrides the URL. Defaults to the filename minus the date |

The slug becomes the URL: `ventura.energy/updates/<slug>.html`. Once a post is
public, do not change its slug, or existing links to it break.

**Body syntax** is deliberately small: `##` and `###` headings, `-` bullets,
blank-line paragraphs, `**bold**`, `*italic*`, `[text](url)`. Anything else is
treated as plain text. There is no support for images in posts yet.

## Build and publish

```bash
python tools/buildsite.py
git add -A
git commit -m "Post: what the 2026 rate case means for pumping costs"
git push
```

The build fails loudly rather than publishing something broken. It stops if the
front matter is missing, the date is not `YYYY-MM-DD`, the slug has characters
that do not belong in a URL, two posts claim the same slug, or a file has no
body.

## What the build touches

It rewrites the HTML pages and `assets/site.css` and `assets/site.js`. It leaves
`assets/img/` and `assets/fonts/` alone once they exist, so photographs are never
re-copied or overwritten by a build.

Source lives in `tools/`: `buildsite.py` builds the pages, `posts_md.py` reads
the markdown, `site.css` and `site.js` are the originals that get copied into
`assets/`. **Edit `tools/site.css`, not `assets/site.css`**, or the next build
overwrites your change.

## Checking before you push

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/updates.html` and click through to the new post.

Worth a look every time: the post appears at the top of the updates list, the
date reads correctly, and headings and bullets came out as headings and bullets
rather than paragraphs.

## Removing a post

Delete the markdown file and rebuild. The HTML file it produced stays behind, so
delete that too:

```bash
rm content/posts/2026-09-15-some-slug.md
rm updates/some-slug.html
python tools/buildsite.py
```
