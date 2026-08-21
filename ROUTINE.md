# Monthly blog post: handover to the routine runner

What the routine has to do, once a month, and how to tell whether it worked.

## The job in one line

Turn a written post into a markdown file in the site repo, build, commit, push.
GitHub Pages redeploys on its own.

## Environment the routine needs

| Thing | Value |
|---|---|
| Repo | `cnmve24/ventura-energy-site` |
| Local clone | `C:\Users\clara\ventura-energy-site` |
| Branch | `main` |
| Python | any 3.x already on the machine, no packages needed |
| Auth | Git Credential Manager already holds a working token for `cnmve24`. `gh` itself is broken, so the routine should use plain `git`, not `gh` |

If the clone is missing, recreate it with
`git clone https://github.com/cnmve24/ventura-energy-site.git`.

## Steps

```bash
cd C:\Users\clara\ventura-energy-site
git pull

# 1. write the post to content/posts/YYYY-MM-DD-slug.md
# 2. build
python tools/buildsite.py

# 3. publish
git add -A
git commit -m "Post: <title>"
git push
```

The file format is in `POSTING.md` in the repo. Front matter needs `title` and
`date`; the body understands `##` and `###` headings, `-` bullets, blank-line
paragraphs, `**bold**`, `*italic*`, and `[links](url)`.

## How the routine knows it worked

Three checks, in order of how much they tell you:

1. **The build printed `built N pages`.** If front matter is malformed the build
   exits with a message naming the file and the problem, and writes nothing.
2. **`git push` returned cleanly.**
3. **The post is live.** Wait a minute or two, then:

```bash
curl -s -o /dev/null -w "%{http_code}" https://ventura.energy/updates/<slug>.html
```

`200` means published. `404` means Pages has not finished, or the slug does not
match the file that was built.

## Things that will go wrong eventually

**Two posts with the same slug.** The build stops and names both files. Change
one slug and rebuild.

**A slug that changed after publishing.** The old HTML file stays on disk and
keeps serving at the old URL while the new one appears too, so the same post is
live at two addresses. Delete the stale file from `updates/` and rebuild.

**Pull before push.** If a post is written on one machine and the site edited on
another, `git push` is rejected. `git pull --rebase` then push again.

**Nothing to commit.** Means the markdown file was not actually written to
`content/posts/`, or was written outside the repo.

## What the routine must not do

- **Do not edit `assets/site.css`.** It is overwritten by every build. The real
  file is `tools/site.css`.
- **Do not delete anything in `assets/img/`.** The build never re-copies
  photographs once they exist, so a deleted image is gone from the site until
  someone restores it from the Drive.
- **Do not touch DNS or the `CNAME` file.** The domain is live and pointed.
- **Do not force push.**

## Judgment calls that are not the routine's to make

A monthly cadence on a site whose previous posts stopped in 2022 is the point of
the exercise, so publishing on schedule matters more than any individual post
being perfect. But two things are worth a human eye before they go public,
because the site is live at ventura.energy and the repository is public:

- **Anything naming a client site.** The standing rule is that individual project
  sites are not named publicly: no host names, no addresses, no well numbers.
  Categories are fine, "a water district" rather than the district.
- **Anything asserting current policy.** Rate structures and incentive programs
  move, and two of the existing posts are already out of date because of it. A
  post that states what a tariff does today should have been checked today.

## Where everything else lives

`Company Docs\Website\` in the company Drive: the copy documents, the photo
caption sheet, full resolution photography, and a copy of the site source.
