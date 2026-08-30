"""Build the static site for GitHub Pages: real pages, real asset files."""
import os, re, sys, json, shutil, html as H

# Run this from the repository root: python tools/buildsite.py
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SRC = 'tools'
OUT = '.'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import posts_md

POSTS = posts_md.load()
ORDER = posts_md.order(POSTS)
SLUG = {k: k for k in POSTS}
pretty_date = posts_md.pretty_date
ENTS = {'’': '&rsquo;', '‘': '&lsquo;', '“': '&ldquo;',
        '”': '&rdquo;', '§': '&sect;', '—': ', ', '–': '-'}


def esc(t):
    t = H.escape(t, quote=True)
    for ch, ent in ENTS.items():
        t = t.replace(ch, ent)
    return t


# ---------------------------------------------------------------- scaffolding
def head(title, desc, depth=0):
    up = '../' * depth
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{up}assets/site.css">
<link rel="icon" href="{up}assets/img/favicon.png">
</head>
<body>
'''


def nav(active, depth=0, over_photo=False):
    up = '../' * depth
    items = [('Projects', up + 'projects.html', 'projects'),
             ('Updates', up + 'updates.html', 'updates')]
    current = ' aria-current="page"'
    links = ''.join(
        f'<li><a href="{href}"{current if key == active else ""}>{label}</a></li>'
        for label, href, key in items)
    bar = f'''<div class="sitenav">
  <a href="{up}index.html"><img src="{up}assets/img/logo-white.png" alt="Ventura Energy" width="96" height="81"></a>
  <ul>{links}<li><a class="navcta" href="mailto:info@ventura.energy">Get started</a></li></ul>
</div>'''
    return bar if over_photo else f'<div class="topbar">{bar}</div>'


MAIL_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<rect x="3" y="5" width="18" height="14" rx="2"/>'
             '<path d="m3.5 7 8.5 6 8.5-6"/></svg>')


def footer(depth=0):
    up = '../' * depth
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="foot-brand">
      <img src="{up}assets/img/logo-white.png" alt="" width="76" height="64">
      <p class="foot-name">Ventura Energy LLC</p>
      <address class="foot-addr">925 De La Vina Street, Ste 104<br>Santa Barbara, CA 93101</address>
    </div>
    <nav class="foot-nav" aria-label="Footer">
      <p class="foot-label">Site</p>
      <a href="{up}index.html">Home</a>
      <a href="{up}projects.html">Projects</a>
      <a href="{up}updates.html">Updates</a>
    </nav>
    <nav class="foot-nav" aria-label="Affiliates">
      <p class="foot-label">Affiliates</p>
      <a href="https://www.venturaenergypartners.com/" target="_blank" rel="noopener noreferrer">Ventura Energy Partners</a>
      <a href="https://www.vepce.energy/" target="_blank" rel="noopener noreferrer">Ventura Energy Partners, Central Europe</a>
    </nav>
    <a class="foot-contact" href="mailto:info@ventura.energy">
      <span class="ico">{MAIL_ICON}</span>
      <span>info@ventura.energy</span>
    </a>
  </div>
  <div class="foot-legal"><div class="wrap">
    <span>Ventura Energy LLC</span>
  </div></div>
</footer>
<script src="{up}assets/site.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- page bodies
def img(name, alt, cls='', extra=''):
    return f'<img src="assets/img/{name}" alt="{esc(alt)}" {cls and f"class={cls} "}{extra}>'


ALTS = {
 1: 'Two solar-covered reservoirs with green hills behind',
 2: 'Solar array on a covered reservoir bordered by citrus orchard and open field',
 3: 'Covered reservoir beside the rail line, valley and mountains beyond',
 4: 'Both reservoir covers seen across orchards and row crops',
 5: 'Overhead view of the two solar-covered reservoirs and surrounding fields',
 6: 'Close overhead detail of panel rows across the reservoir cover',
 7: 'Low aerial across the covers toward the green coastal range',
 8: 'Covered reservoir with palms and yard in the foreground',
 9: 'Covered reservoir with irrigation pipe stacks in the yard below',
 10: 'Both covers with equipment yard and orchards to the east',
 11: 'The two covers centered under the mountains, midday light',
 12: 'The covers looking down valley toward the coast',
 13: 'Covered reservoir framed by palms and avocado orchard',
 14: 'Both covers and the staging yard, hills across the valley',
}
WIDE = {5, 11}

SLIDES = [
 ('lift',  'A battery being delivered', 'A large battery enclosure suspended from a crane on spreader bars above a prepared pad'),
 ('pump',  'Energy storage system at a pump station', 'A long white battery enclosure on a fresh gravel pad beside a road, trees behind'),
 ('well3', 'Energy storage system at a well site', 'A row of white battery and inverter cabinets on gravel, orchard and hills behind'),
 ('crane', 'Setting the first unit', 'A crane working beside a prepared pad with an enclosure rigged for lifting'),
 ('cmwc',  'Commissioning in progress', 'A technician in high-visibility clothing working at a row of battery cabinets, mountains behind'),
 ('lower', 'Lowering onto the pad', 'A battery enclosure being lowered by crane onto a concrete pad at a well site'),
 ('well2', 'Small battery site in Ventura County', 'Close view of battery cabinets behind yellow bollards'),
]
BUILDS = [
 ('rows',    'Single axis tracking system', 'A long row of solar modules on single-axis trackers, dry ground beneath'),
 ('slope',   'Solar rows following a slope', 'Solar rows following a hillside with the valley floor beyond'),
 ('close',   'Modules and foundations', 'Solar modules seen close, steel piles set into red earth'),
 ('canopy1', 'Canopy steel going up', 'The steel frame of a solar canopy before the modules are set, palms and hills behind'),
 ('canopy2', 'First modules on the solar canopy', 'Solar modules being laid onto the canopy frame under a clear sky'),
 ('canopy3', 'Solar canopy nearly completed', 'A solar canopy with most of its modules installed, mountains in the distance'),
]
LEGACY = [
 ('Alcatraz Island, California', 'Aerial of Alcatraz Island with a rooftop solar array on the main cellhouse', True),
 ('Utility-scale farm, southeastern United States', 'Aerial of a large ground-mount solar farm bordered by pine forest', False),
 ('Utility-scale farm, southeastern United States', 'Aerial of solar rows crossing cleared farmland', False),
 ('Utility-scale farm, southeastern United States', 'Aerial of long solar rows following the contour of the land', False),
 ('Single-axis tracker rows, Montana', 'Ground view of tracker-mounted panels in a mountain meadow', False),
 ('Ballasted rooftop array, Colorado', 'Rooftop panels on ballasted racking with autumn trees behind', False),
 ('Thin-film modules, desert site, Moapa, Nevada', 'Close view of thin-film modules with desert mountains beyond', False),
 ('Ground-mount array, Central Valley, CA', 'Ground-mount panel row on desert sand under transmission lines', False),
]
SERVICES = [
 ('01', 'Site evaluation', 'Does this actually make sense for you? We answer that first, with your real utility bills.'),
 ('02', 'Design &amp; engineering', 'Renewable and resilient system design sized to how your operation really runs.'),
 ('03', 'Permitting', 'Local jurisdictions, utility interconnection, and the paperwork nobody enjoys.'),
 ('04', 'Project &amp; construction management', 'One accountable party from notice to proceed through commissioning.'),
 ('05', 'Operations &amp; monitoring', 'Production and savings tracked continuously, so you see what the system earns.'),
 ('06', 'Incentives &amp; grants', 'SGIP, feed-in tariffs, and grant feasibility and applications, start to finish.'),
 ('07', 'Financing &amp; ownership', 'We can own and operate the system for its life. You put in $0 and pay us less than the utility, or we pay you a lease.'),
 ('08', 'Advisory &amp; development consulting', 'For developers and owners running their own projects: the same work, under your name instead of ours.'),
]
WHY = [
 ('ROI positive from day one', 'Structured so the savings exceed the payment in the first month, not the seventh year.'),
 ('Protect critical operations', "Pumps, cooling, and packing don't stop when the grid does."),
 ('Beat your electric bills at their own game', "Peak pricing is only expensive if you're buying during peak."),
]


def home():
    stats = [('15+ years', 'Developing renewable projects'),
             ('1 GW+', 'Capacity developed &amp; advised'),
             ('3.5 GWh', 'Storage developed &amp; advised'),
             ('Two dozen+', 'Owned &amp; operated locally')]
    p = head('Ventura Energy | Storage and solar for businesses and landowners',
             'Ventura Energy develops, owns and operates solar and energy storage for businesses and landowners in Ventura County and beyond.')
    p += f'''<header class="hero">
  <img class="bg" src="assets/img/hero.jpg" alt="Aerial view of solar arrays on two covered reservoirs in the Santa Clara River Valley, green hills behind">
  {nav('home', over_photo=True)}
  <div class="wrap rise">
    <p class="eyebrow">Your local energy experts</p>
    <h1>Power up your business with energy savings</h1>
    <p class="lede">Storage and solar for businesses and landowners. Evaluated honestly, built locally, and operated for the life of the system.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="mailto:info@ventura.energy">See if it pencils for you</a>
      <a class="btn btn-ghost" href="projects.html">View projects</a>
    </div>
  </div>
  <span class="credit">Photography by Motive Marketing</span>
</header>

<div class="stats"><div class="wrap">
'''
    p += ''.join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in stats)
    p += '''</div></div>

<section class="band">
  <div class="wrap split">
    <div class="rise">
      <p class="eyebrow on-light">Who we are</p>
      <h2 class="section-title">Developed and deployed worldwide.<br>Owned and operated locally.</h2>
      <div class="body-copy">
        <p>Over fifteen years, thousands of sites, and gigawatts of projects behind us. We develop <strong>solar, storage, and microgrid technology</strong> worldwide.</p>
        <p>Locally, we are an <strong>independent power producer</strong>. We own and operate the solar and storage we build. The benefit lands where it should: with the business paying the utility bill, or the landowner collecting a lease.</p>
      </div>
    </div>
    <figure class="figure rise">
      <img src="assets/img/side.jpg" alt="Overhead view of the two solar-covered reservoirs bordered by citrus orchard and open field">
      <figcaption>Santa Clara River Valley, Ventura County</figcaption>
    </figure>
  </div>
</section>

<section class="band services">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow on-light">What we do</p>
      <h2 class="section-title">Protect business operations</h2>
      <p class="lede" style="margin-top:20px;color:var(--text-soft)">A full suite of renewable and resilient energy services. We can run the whole project, or step in where you need us.</p>
    </div>
    <div class="svc-grid rise">'''
    p += ''.join(f'<div class="svc"><span class="n">{n}</span><h3>{t}</h3><p>{d}</p></div>'
                 for n, t, d in SERVICES)
    p += '''</div>
  </div>
</section>

<section class="band why">
  <img class="bg" src="assets/img/strip.jpg" alt="">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow">Why now</p>
      <h2 class="section-title">Solar projects don't save money anymore.<br>Solar-and-storage projects do.</h2>
      <p class="lede" style="margin-top:20px">We specialize in storage, with a long history of solar expertise behind it, so your project maximizes both your savings and your operational resilience.</p>
    </div>
    <div class="why-grid rise">'''
    p += ''.join(f'<div class="why-item"><h3>{t}</h3><p>{d}</p></div>' for t, d in WHY)
    p += '''</div>
  </div>
</section>

<section class="band promise">
  <div class="wrap rise">
    <div class="rule"></div>
    <blockquote>Most sites don't pencil.</blockquote>
    <p>We will tell you that early, and for free. We live here, and a project that doesn't work is a neighbor we lose. But when a site does pencil, that is money you stop sending out the door every month, for the next twenty years.</p>
  </div>
</section>

<section class="band cta">
  <div class="wrap rise">
    <h2>Start a conversation</h2>
    <p>Reach out to see what is possible for your business or for your land.</p>
    <a class="btn btn-primary" href="mailto:info@ventura.energy">Get started</a>
  </div>
</section>
'''
    return p + footer()


def projects():
    p = head('Projects | Ventura Energy',
             'Solar and energy storage projects developed, owned and operated by Ventura Energy.')
    p += nav('projects')
    p += '''<section class="band feature">
  <div class="wrap split">
    <figure class="figure rise">
      <img src="assets/img/feat.jpg" alt="Overhead view of the two solar-covered reservoirs, orchards and open field around them">
    </figure>
    <div class="rise">
      <p class="eyebrow on-light">Featured project</p>
      <h2 class="section-title">Solar &amp; water</h2>
      <div class="body-copy">
        <p>A century-old grower cooperative is converting its water system from gravity-fed canals to pressurized distribution: precise delivery to every parcel, far less lost to evaporation and seepage. Pressure costs electricity, and electricity rates directly affect the ability of farming to pencil in Ventura County.</p>
        <p>The solar system was built on top of <strong>two new reservoir covers</strong>. The energy generation pays for the pumping. No land acreage taken out of production, and millions in projected net savings passed straight through to the member growers.</p>
      </div>
      <dl class="spec">
        <div><dt>Installed on</dt><dd>Two new reservoir covers</dd></div>
        <div><dt>Utility program</dt><dd>SCE NEM 2.0</dd></div>
        <div><dt>Structure</dt><dd>Power purchase agreement</dd></div>
        <div><dt>Our role</dt><dd>Developer, owner of renewable energy credits</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="band gallery">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow on-light">Project gallery</p>
      <h2 class="section-title">From the air</h2>
      <p class="lede" style="margin-top:20px;color:var(--text-soft)">Two covered reservoirs carrying the array that pumps them. Photographed February 2026.</p>
    </div>
    <div class="grid rise">'''
    p += ''.join(
        f'<button class="{"shot wide" if n in WIDE else "shot"}" data-cap="Frame {n:02d} of 14" type="button">'
        f'<img src="assets/img/aerial-{n:02d}.jpg" alt="{esc(ALTS[n])}" loading="lazy">'
        f'<span class="num">{n:02d}</span></button>' for n in range(1, 15))
    p += '''</div>
  </div>
</section>

<section class="band resil">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow">Energy resiliency for water</p>
      <h2 class="section-title">When the power goes out,<br>will there still be water?</h2>
      <p class="lede" style="margin-top:20px">Much of Ventura County's water comes from wells, and electricity runs the pumps. After the Thomas Fire took down lines across the county in December 2017 and cut power to water pumping facilities, we built a fleet of battery storage systems at water well sites so the pumps can keep running when the grid doesn't.</p>
      <p class="lede" style="margin-top:16px">All developed and operated by us, the majority owned by us, and every one within a short drive of the office.</p>
    </div>
    <div class="slider rise">
      <div class="slides" id="resilSlides" tabindex="0" role="group" aria-label="Photographs of storage at water sites">'''
    p += ''.join(f'<figure class="slide" data-cap="{esc(cap)}">'
                 f'<img src="assets/img/slide-{k}.jpg" alt="{esc(alt)}"></figure>'
                 for k, cap, alt in SLIDES)
    p += '''</div>
      <button class="sl-nav sl-prev" type="button" aria-label="Previous photo">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7"/></svg>
      </button>
      <button class="sl-nav sl-next" type="button" aria-label="Next photo">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>
      </button>
      <div class="sl-bar">
        <span class="sl-cap" id="resilCap"></span>
        <div class="sl-dots" id="resilDots"></div>
      </div>
    </div>
  </div>
</section>

<section class="band build">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow on-light">Under construction</p>
      <h2 class="section-title">Going in now</h2>
      <p class="lede" style="margin-top:20px;color:var(--text-soft)">Ground mount tracking system for an industrial poultry processor, a solar carport for an irrigation company, and other energy storage projects for a water company.</p>
    </div>
    <div class="grid rise">'''
    p += ''.join(f'<button class="shot" data-cap="{esc(cap)}" type="button">'
                 f'<img src="assets/img/build-{k}.jpg" alt="{esc(alt)}" loading="lazy">'
                 f'<span class="cap">{esc(cap)}</span></button>' for k, cap, alt in BUILDS)
    p += '''</div>
  </div>
</section>

<section class="band past">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow on-light">Past projects</p>
      <h2 class="section-title">The work that got us here</h2>
      <p class="lede" style="margin-top:20px;color:var(--text-soft)">Ventura Energy opened its doors in 2021, on the back of more than a decade spent designing and building solar, from single rooftops to projects covering thousands of acres. The energy storage work started in 2018, alongside the idea that has since come to be called the virtual power plant.</p>
    </div>
    <div class="grid rise">'''
    p += ''.join(f'<button class="{"shot wide" if w else "shot"}" data-cap="{esc(cap)}" type="button">'
                 f'<img src="assets/img/legacy-{i:02d}.jpg" alt="{esc(alt)}" loading="lazy">'
                 f'<span class="cap">{esc(cap)}</span></button>'
                 for i, (cap, alt, w) in enumerate(LEGACY, 1))
    p += '''</div>
  </div>
</section>

<dialog class="lb" id="lb">
  <img id="lb-img" alt="">
  <div class="bar"><span id="lb-cap"></span><button id="lb-close" autofocus>Close</button></div>
</dialog>
'''
    return p + footer()


def updates_index():
    p = head('Updates | Ventura Energy',
             'Market and industry updates from Ventura Energy: rate cases, tariffs, incentives and storage economics in California.')
    p += nav('updates')
    p += '''<section class="band updates">
  <div class="wrap">
    <div class="rise">
      <p class="eyebrow on-light">Updates</p>
      <h2 class="section-title">Market updates,<br>and things to watch</h2>
      <p class="lede" style="margin-top:20px;color:var(--text-soft)">Rate cases and tariff decisions, incentive programs opening and closing, interconnection queues, equipment supply, and the economics of storage. The developments shaping what gets built in California, and what they mean for the districts and growers who have to live with them.</p>
    </div>
    <div class="post-list rise">'''
    p += ''.join(f'<a class="post" href="updates/{SLUG[k]}.html">'
                 f'<time>{esc(pretty_date(POSTS[k]["date"]))}</time><h3>{esc(POSTS[k]["title"])}</h3></a>'
                 for k in ORDER)
    p += '''</div>
  </div>
</section>
'''
    return p + footer()


def article(k):
    d = POSTS[k]
    out, open_list = [], False
    for b in d['blocks']:
        tag, text = b['tag'], posts_md.inline(esc(b['text']))
        if tag == 'li':
            if not open_list:
                out.append('<ul>'); open_list = True
            out.append(f'<li>{text}</li>'); continue
        if open_list:
            out.append('</ul>'); open_list = False
        if tag == 'h1':
            tag = 'h2'
        if tag == 'note':
            out.append(f'<aside class="art-note">{text}</aside>')
        else:
            out.append(f'<{tag}>{text}</{tag}>')
    if open_list:
        out.append('</ul>')
    first = next((b['text'] for b in d['blocks'] if b['tag'] == 'p'), '')
    p = head(d['title'] + ' | Ventura Energy', first[:155], depth=1)
    p += nav('updates', depth=1)
    p += f'''<section class="band article">
  <div class="wrap">
    <div class="art-head rise">
      <p class="art-meta">{esc(pretty_date(d["date"]))} &middot; Clara Nagy McBane</p>
      <h1 class="art-title">{esc(d["title"])}</h1>
    </div>
    <div class="art-body rise">{"".join(out)}</div>
    <div class="art-foot rise">
      <a class="art-back" href="../updates.html">All updates</a>
      <a class="art-back" href="../index.html">Ventura Energy</a>
    </div>
  </div>
</section>
'''
    return p + footer(depth=1)


# ---------------------------------------------------------------- assemble
os.makedirs(f'{OUT}/assets/img', exist_ok=True)
os.makedirs(f'{OUT}/assets/fonts', exist_ok=True)
os.makedirs(f'{OUT}/updates', exist_ok=True)

shutil.copy(f'{SRC}/site.css', f'{OUT}/assets/site.css')
for w in (300, 400, 500, 600):
    dst = f'{OUT}/assets/fonts/poppins-{w}.woff2'
    if not os.path.exists(dst):
        shutil.copy(f'{SRC}/fonts/poppins-{w}.woff2', dst)

# images, renamed to something a human can read in a repo
copies = {'hero.jpg': 'hero.jpg', 'strip.jpg': 'strip.jpg', 'feat.jpg': 'feat.jpg',
          'side.jpg': 'side.jpg', 'logo-white.png': 'logo-white.png'}
for n in range(1, 15):
    copies[f'thumb{n:02d}.jpg'] = f'aerial-{n:02d}.jpg'
for k, _, _ in SLIDES:
    copies[f'slide_{k}.jpg'] = f'slide-{k}.jpg'
for k, _, _ in BUILDS:
    copies[f'build_{k}.jpg'] = f'build-{k}.jpg'
for i in range(1, 9):
    copies[f'legacy{i:02d}.jpg'] = f'legacy-{i:02d}.jpg'
for src, dst in copies.items():
    target = f'{OUT}/assets/img/{dst}'
    if not os.path.exists(target):
        shutil.copy(f'{SRC}/assets/{src}', target)

# a small favicon from the logo
if not os.path.exists(f'{OUT}/assets/img/favicon.png'):
  from PIL import Image
  ico = Image.open(f'{SRC}/assets/logo-navy.png').convert('RGBA')
  bg = Image.new('RGBA', ico.size, (255, 255, 255, 255))
  bg.alpha_composite(ico)
  bg.convert('RGB').resize((64, 64), Image.LANCZOS).save(f'{OUT}/assets/img/favicon.png')

open(f'{OUT}/index.html', 'w', encoding='utf-8').write(home())
open(f'{OUT}/projects.html', 'w', encoding='utf-8').write(projects())
open(f'{OUT}/updates.html', 'w', encoding='utf-8').write(updates_index())
for k in ORDER:
    open(f'{OUT}/updates/{SLUG[k]}.html', 'w', encoding='utf-8').write(article(k))

open(f'{OUT}/.nojekyll', 'w').write('')
shutil.copy(f'{SRC}/site.js', f'{OUT}/assets/site.js')

total = sum(os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(OUT) for f in fs)
pages = [f for r, _, fs in os.walk(OUT) for f in fs if f.endswith('.html')]
print(f'built {len(pages)} pages, {total/1024/1024:.1f} MB total')
for r, _, fs in sorted(os.walk(OUT)):
    for f in sorted(fs):
        if f.endswith('.html'):
            print('  ', os.path.join(r, f).replace(OUT + os.sep, ''))
