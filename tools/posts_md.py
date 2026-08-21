"""Read blog posts from markdown files.

One file per post in content/posts/. Front matter sets the title and date;
the body is a small subset of markdown: ## and ### headings, - bullets,
blank-line separated paragraphs, **bold**, *italic*, and [links](url).

The slug decides the URL. It comes from the front matter if given, otherwise
from the filename with any leading date stripped, so renaming a file does not
silently move a published page.
"""
import os
import re

MONTHS = ('January February March April May June July August September '
          'October November December').split()

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
FRONT_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.S)
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
ITAL_RE = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')


def pretty_date(iso):
    y, m, d = iso.split('-')
    return '%s %d, %s' % (MONTHS[int(m) - 1], int(d), y)


def inline(text):
    """Apply inline markdown. Call this after HTML escaping, so any tags
    produced here are ours rather than the author's."""
    text = LINK_RE.sub(lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), text)
    text = BOLD_RE.sub(r'<strong>\1</strong>', text)
    text = ITAL_RE.sub(r'<em>\1</em>', text)
    return text


def _parse_body(body):
    blocks, para = [], []

    def flush():
        if para:
            blocks.append({'tag': 'p', 'text': ' '.join(para)})
            para.clear()

    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith('### '):
            flush(); blocks.append({'tag': 'h3', 'text': line[4:].strip()})
        elif line.startswith('## '):
            flush(); blocks.append({'tag': 'h2', 'text': line[3:].strip()})
        elif line.startswith('- '):
            flush(); blocks.append({'tag': 'li', 'text': line[2:].strip()})
        else:
            para.append(line.strip())
    flush()
    return blocks


def load(folder='content/posts'):
    """Return {slug: {title, date, blocks}}. Raises on anything malformed,
    so a bad post stops the build instead of publishing broken."""
    posts = {}
    if not os.path.isdir(folder):
        raise SystemExit('no such folder: ' + folder)
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith('.md'):
            continue
        raw = open(os.path.join(folder, fn), encoding='utf-8').read()
        m = FRONT_RE.match(raw)
        if not m:
            raise SystemExit('%s: needs a front matter block delimited by ---' % fn)
        meta = {}
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip()
        for key in ('title', 'date'):
            if not meta.get(key):
                raise SystemExit('%s: front matter needs a %s' % (fn, key))
        if not DATE_RE.match(meta['date']):
            raise SystemExit('%s: date must be YYYY-MM-DD, got %r' % (fn, meta['date']))
        slug = meta.get('slug') or re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fn[:-3])
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise SystemExit('%s: slug %r should be lowercase letters, numbers and hyphens' % (fn, slug))
        if slug in posts:
            raise SystemExit('%s: slug %r is already used by another post' % (fn, slug))
        blocks = _parse_body(m.group(2))
        if not blocks:
            raise SystemExit('%s: no body content' % fn)
        posts[slug] = {'title': meta['title'], 'date': meta['date'], 'blocks': blocks}
    if not posts:
        raise SystemExit('no .md files found in ' + folder)
    return posts


def order(posts):
    """Newest first."""
    return sorted(posts, key=lambda k: posts[k]['date'], reverse=True)
