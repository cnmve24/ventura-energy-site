# ventura.energy

Static site for Ventura Energy LLC. No build step, no dependencies: the files in
this repository are the site exactly as it is served.

## Pages

| File | Page |
|---|---|
| `index.html` | Home |
| `projects.html` | Projects |
| `updates.html` | Updates index |
| `updates/*.html` | One file per article |

`assets/` holds the stylesheet, one small script, the Poppins web fonts, and the
photography.

## Hosting on GitHub Pages

1. Push this repository to GitHub.
2. Settings, then Pages.
3. Source: **Deploy from a branch**. Branch: `main`, folder: `/ (root)`.
4. Save. The site appears at `https://<account>.github.io/<repo>/` within a minute or two.

Pages on a free account requires the repository to be **public**. Making it
public publishes the photography and copy, so do that when the content is ready
to be seen rather than as a step in setup.

`.nojekyll` is present so GitHub serves the files as they are instead of running
them through Jekyll.

## Moving ventura.energy across from Squarespace

1. In Pages, set the custom domain to `ventura.energy`. That writes a `CNAME` file here.
2. At the DNS host, point the apex at GitHub:
   - `A` records to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - or `ALIAS`/`ANAME` to `<account>.github.io` if the provider supports it
   - `CNAME` for `www` to `<account>.github.io`
3. Wait for the certificate, then tick **Enforce HTTPS**.

Do not cancel Squarespace until the new site resolves and serves over HTTPS.
DNS changes can take a few hours to settle, and the domain is currently billed
through Squarespace, so check where the registration actually lives first.

## Editing

Plain HTML and CSS, so most changes are a text edit away.

- Copy lives in the page files.
- Colours, type, and spacing live in `assets/site.css` as custom properties at the top.
- Photographs live in `assets/img/`. Replace a file with one of the same name and
  the page picks it up. Keep the long edge near 1600px and quality around 80, and
  strip EXIF before committing: several originals carry drone GPS coordinates.

The generator that produced these files, along with the full resolution
photography, is in the company Drive at `Company Docs\Website\`.

## Things still open

- Pages not yet written: About Us, For Your Business, For Your Land, Contact.
- Two articles from 2022 describe policy that has since changed. They are dated
  on the page, but they are out of date.
- The gigawatt and gigawatt-hour figures on the home page are company claims and
  should be checked before this is public.
