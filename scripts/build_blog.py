#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import xml.sax.saxutils as xml_escape
from dataclasses import dataclass
from datetime import date, datetime
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, List, Tuple

SITE_URL = "https://sitoweb.info"
SITE_NAME = "SitoWeb.info"
SITE_DESCRIPTION = "Guide semplici e realizzazione siti web professionali, WordPress, GDPR e sicurezza."
AUTHOR_NAME = "Gabriele Viola"
AUTHOR_EMAIL = "business@gabrieleviola.it"

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"

FIXED_PAGES = [
    {"loc": "/", "priority": "1.0", "changefreq": "weekly", "file": "index.html"},
    {"loc": "/blog.html", "priority": "0.8", "changefreq": "weekly", "file": "blog.html"},
    {"loc": "/privacy-policy.html", "priority": "0.3", "changefreq": "yearly", "file": "privacy-policy.html", "only_if_exists": True},
]

LEGACY_BLOG_ARTICLES = [
    {
        "slug": "quanto-costa-un-sito-web",
        "title": "Quanto costa un sito web?",
        "excerpt": "Una guida chiara per capire cosa incide davvero sul prezzo: dominio, hosting, grafica, testi, SEO, GDPR, sicurezza, manutenzione e assistenza.",
        "icon": "fas fa-euro-sign",
    },
    {
        "slug": "quando-un-sito-web-e-sicuro",
        "title": "Quando un sito web è sicuro?",
        "excerpt": "SSL, aggiornamenti, backup, protezione WordPress, moduli, password, malware, monitoraggio e gestione responsabile dei dati.",
        "icon": "fas fa-shield-halved",
    },
    {
        "slug": "come-avere-un-sito-web-gratis",
        "title": "Come avere un sito web gratis?",
        "excerpt": "WordPress.com, Altervista, Blogger/Blogspot, ForumFree e alternative: quando vanno bene e quando per un'azienda conviene investire.",
        "icon": "fas fa-gift",
    },
]

COMMON_CSS = r"""
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: 'Inter', sans-serif; background: #ffffff; color: #1e1e2f; line-height: 1.6; }
.container { max-width: 1280px; margin: 0 auto; padding: 0 24px; }
header { padding: 20px 0; border-bottom: 1px solid #eef2f6; position: sticky; top: 0; z-index: 50; backdrop-filter: blur(4px); background: rgba(255,255,255,0.88); }
.nav-bar { display: flex; align-items: center; justify-content: space-between; gap: 18px; flex-wrap: wrap; }
.logo { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.03em; color: #0b2b4a; text-decoration:none; }
.logo span { color: #2563eb; }
.nav-links { display: flex; align-items: center; gap: 1.6rem; font-weight: 500; }
.nav-links a { text-decoration: none; color: #1e293b; transition: color 0.2s; }
.nav-links a:hover { color: #2563eb; }
.menu-toggle { display: none; background: none; border: none; font-size: 1.8rem; color: #0b2b4a; cursor: pointer; }
.btn-outline, .btn-primary, .btn-light { padding: 12px 24px; border-radius: 60px; font-weight: 700; text-decoration: none; display: inline-block; transition: all 0.2s ease; border: 1.5px solid #2563eb; text-align: center; }
.btn-outline { background: transparent; color: #2563eb; }
.btn-outline:hover { background: #2563eb; color: #fff; transform: translateY(-2px); }
.btn-primary { background: #2563eb; color: white; box-shadow: 0 12px 18px -8px rgba(37,99,235,0.25); }
.btn-primary:hover { background: #1d4ed8; color: white; transform: translateY(-3px); box-shadow: 0 20px 25px -8px rgba(37,99,235,0.32); }
.btn-light { background: #fff; color: #0b2b4a; border-color: #fff; }
.btn-light:hover { transform: translateY(-2px); box-shadow: 0 14px 24px -12px rgba(0,0,0,0.2); }
section { padding: 82px 0; }
h1, h2, h3 { color: #0b2b4a; letter-spacing: -0.025em; line-height: 1.18; }
h1 { font-size: clamp(2.35rem, 5vw, 4.2rem); font-weight: 800; margin-bottom: 24px; }
h2 { font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 800; margin: 40px 0 16px; }
h3 { font-size: 1.45rem; font-weight: 750; margin: 28px 0 12px; }
p { color: #475569; }
.hero { padding: 56px 0 70px; display: flex; align-items: center; flex-wrap: wrap; gap: 46px; }
.hero-content { flex: 1 1 520px; }
.hero-sub { font-size: 1.22rem; color: #475569; margin-bottom: 30px; max-width: 790px; }
.hero-highlight { color: #2563eb; border-bottom: 4px solid #93c5fd; }
.badge { background: #dbeafe; color: #1e40af; padding: 7px 15px; border-radius: 30px; font-weight: 700; font-size: 0.92rem; display: inline-block; margin-bottom: 20px; }
.card { background: white; border-radius: 28px; padding: 32px 24px; box-shadow: 0 15px 30px -14px rgba(15,23,42,0.1); border: 1px solid #eef2f6; transition: all 0.25s; }
.card:hover { transform: translateY(-7px); box-shadow: 0 25px 35px -16px rgba(37,99,235,0.18); border-color: #bfdbfe; }
.card-icon { font-size: 2.5rem; color: #2563eb; margin-bottom: 18px; }
.soft-bg { background: #fafcff; }
.blue-bg { background: #0b2b4a; color: white; }
.blue-bg h2, .blue-bg h3, .blue-bg p { color: white; }
.blue-bg p { opacity: 0.9; }
.blog-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:26px; margin-top:34px; }
.blog-grid .card { display:flex; flex-direction:column; }
.blog-grid .card p { flex:1; }
.blog-grid .card a { color:#2563eb; font-weight:700; text-decoration:none; }
.breadcrumb { font-size:0.95rem; margin-bottom:18px; color:#64748b; }
.breadcrumb a { color:#2563eb; text-decoration:none; font-weight:700; }
.article-wrap { max-width: 900px; margin: 0 auto; }
.article-meta { color:#64748b; font-weight:600; margin-bottom:18px; }
.article-content { background:white; border:1px solid #eef2f6; border-radius:32px; padding: clamp(26px, 4vw, 46px); box-shadow: 0 20px 44px -28px rgba(15,23,42,0.18); }
.article-content p { margin: 14px 0; font-size:1.08rem; }
.article-content ul, .article-content ol { margin: 16px 0 20px 24px; color:#334155; }
.article-content li { margin: 8px 0; }
.article-content strong { color:#0b2b4a; }
.article-content a { color:#2563eb; font-weight:700; }
.cta-box { margin-top:36px; background:#0b2b4a; color:#fff; padding:32px; border-radius:28px; }
.cta-box h2, .cta-box p { color:#fff; }
.cta-box h2 { margin-top:0; }
footer { background: #0b2b4a; color: #e2e8f0; padding: 44px 0; }
footer a { color: #bfdbfe; text-decoration: none; }
.footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px,1fr)); gap: 30px; }
footer p { color:#dbeafe; margin-top:10px; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }
@media (max-width: 768px) {
  .nav-bar { position:relative; }
  .nav-links { display:none; position:absolute; top:100%; left:0; width:100%; background:white; flex-direction:column; gap:1.2rem; padding:20px; border-top:1px solid #eef2f6; box-shadow:0 10px 20px rgba(0,0,0,0.05); z-index:100; }
  .nav-links.active { display:flex; }
  .menu-toggle { display:block; }
  section { padding: 62px 0; }
}
"""

HEADER = """
<header>
  <div class="container nav-bar">
    <a class="logo" href="index.html">SitoWeb<span>.info</span></a>
    <button class="menu-toggle" id="menuToggle" aria-label="Apri menu"><i class="fas fa-bars"></i></button>
    <div class="nav-links" id="navLinks">
      <a href="index.html#cos-e">Cos'è un sito</a>
      <a href="index.html#ai">Siti e AI</a>
      <a href="blog.html">Blog</a>
      <a href="index.html#pacchetti">Pacchetti</a>
      <a href="index.html#contatti">Contatti</a>
    </div>
    <a href="index.html#contatti" class="btn-outline">Richiedi preventivo</a>
  </div>
</header>
"""

FOOTER = """
<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="logo" style="color: white;">SitoWeb<span style="color: #93c5fd;">.info</span></div>
        <p>Guide semplici e realizzazione siti web professionali, WordPress, GDPR e sicurezza.</p>
        <p>© 2026 SitoWeb.info – P.IVA 02640890220</p>
      </div>
      <div>
        <h4>Link utili</h4>
        <p><a href="index.html#cos-e">Cos'è un sito web</a></p>
        <p><a href="blog.html">Blog e guide</a></p>
        <p><a href="index.html#pacchetti">Pacchetti e prezzi</a></p>
      </div>
      <div>
        <h4>Legale</h4>
        <p><a href="privacy-policy.html">Privacy e Cookie Policy</a></p>
        <p><a href="https://www.iubenda.com/termini-e-condizioni/26348951">Termini e condizioni</a></p>
      </div>
      <div>
        <h4>Contatti</h4>
        <p><a href="mailto:business@gabrieleviola.it">business@gabrieleviola.it</a></p>
        <p><a href="https://www.linkedin.com/in/gabriele-viola/">LinkedIn</a></p>
      </div>
    </div>
    <hr style="border-color: #334155;">
    <p style="text-align: center; font-size: 0.9rem;"><a href="https://www.gabrieleviola.it/">SitoWeb.info — Il sito web giusto, spiegato semplice. Di gabrieleviola.it</a></p>
  </div>
</footer>
<script>
  const toggleBtn = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => navLinks.classList.toggle('active'));
    document.querySelectorAll('.nav-links a').forEach(link => link.addEventListener('click', () => navLinks.classList.remove('active')));
  }
</script>
"""

@dataclass
class Article:
    slug: str
    title: str
    description: str
    excerpt: str
    date: str
    updated: str
    priority: str
    icon: str
    body_html: str


def clean_url(path: str) -> str:
    if path == "/":
        return SITE_URL + "/"
    return SITE_URL.rstrip("/") + "/" + path.lstrip("/")


def parse_front_matter(text: str, source: Path) -> Tuple[Dict[str, str], str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        raise ValueError(f"{source.name}: manca il front matter iniziale delimitato da ---")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"{source.name}: manca il delimitatore finale --- del front matter")

    fm = parts[0].removeprefix("---\n")
    body = parts[1]
    meta: Dict[str, str] = {}

    for line in fm.strip().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.strip()


def inline_markdown(s: str) -> str:
    escaped = html.escape(s)

    # Link: [testo](https://...)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        r'<a href="\2" rel="noopener noreferrer">\1</a>',
        escaped,
    )

    # Grassetto: **testo**
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)

    # Corsivo semplice: *testo*
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)

    return escaped


def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.startswith("### "):
            out.append(f"<h3>{inline_markdown(line[4:].strip())}</h3>")
            i += 1
            continue

        if line.startswith("## "):
            out.append(f"<h2>{inline_markdown(line[3:].strip())}</h2>")
            i += 1
            continue

        if line.startswith("# "):
            out.append(f"<h2>{inline_markdown(line[2:].strip())}</h2>")
            i += 1
            continue

        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline_markdown(lines[i][2:].strip())}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                item = re.sub(r"^\d+\.\s+", "", lines[i]).strip()
                items.append(f"<li>{inline_markdown(item)}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        para = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].startswith(("# ", "## ", "### ", "- "))
            and not re.match(r"^\d+\.\s+", lines[i])
        ):
            para.append(lines[i].strip())
            i += 1

        out.append(f"<p>{inline_markdown(' '.join(para))}</p>")

    return "\n".join(out)


def load_articles() -> List[Article]:
    articles: List[Article] = []
    ARTICLES_DIR.mkdir(exist_ok=True)

    for path in sorted(ARTICLES_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)

        slug = meta.get("slug") or path.stem
        slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-") or path.stem

        title = meta.get("title") or slug.replace("-", " ").title()
        description = meta.get("description") or meta.get("excerpt") or title
        excerpt = meta.get("excerpt") or description
        created = meta.get("date") or date.today().isoformat()
        updated = meta.get("updated") or created
        priority = meta.get("priority") or "0.85"
        icon = meta.get("icon") or "fas fa-file-alt"

        articles.append(
            Article(
                slug=slug,
                title=title,
                description=description,
                excerpt=excerpt,
                date=created,
                updated=updated,
                priority=priority,
                icon=icon,
                body_html=markdown_to_html(body),
            )
        )

    # Nuovi/aggiornati sopra, in ordine cronologico.
    articles.sort(key=lambda a: (a.updated, a.date, a.slug), reverse=True)
    return articles


def html_page(title: str, description: str, canonical_path: str, main_html: str, og_type: str = "website", extra_head: str = "") -> str:
    canonical = clean_url(canonical_path)
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS" href="{SITE_URL}/rss.xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <style>{COMMON_CSS}</style>
{extra_head}
</head>
<body>
{HEADER}
<main>
{main_html}
</main>
{FOOTER}
</body>
</html>
"""


def article_card(slug: str, title: str, excerpt: str, icon: str, updated: str | None = None) -> str:
    meta = f'<p class="article-meta">Aggiornato: {html.escape(updated)}</p>' if updated else ""
    return f"""
      <article class="card">
        <div class="card-icon"><i class="{html.escape(icon)}"></i></div>
        {meta}
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(excerpt)}</p>
        <a href="{html.escape(slug)}.html">Leggi articolo <i class="fas fa-arrow-right"></i></a>
      </article>"""


def build_blog(articles: List[Article]) -> None:
    cards: List[str] = []
    article_slugs = {a.slug for a in articles}

    # Prima i contenuti nuovi generati dai Markdown.
    for a in articles:
        cards.append(article_card(a.slug, a.title, a.excerpt, a.icon, a.updated))

    # Poi gli articoli storici creati a mano, evitando duplicati.
    for a in LEGACY_BLOG_ARTICLES:
        if a["slug"] in article_slugs:
            continue
        if not (ROOT / f"{a['slug']}.html").exists():
            continue
        cards.append(article_card(a["slug"], a["title"], a["excerpt"], a["icon"]))

    total_articles = len(cards)
    main = f"""
  <section class="soft-bg">
    <div class="container article-wrap">
      <div class="breadcrumb"><a href="index.html">Home</a> / Blog</div>
      <span class="badge"><i class="fas fa-book-open"></i> {total_articles} guide pratiche</span>
      <h1>Blog SitoWeb.info: guide semplici per scegliere il sito giusto</h1>
      <p class="hero-sub">Approfondimenti su costi, sicurezza, SEO, AI, hosting e soluzioni gratuite o professionali. Ogni articolo è pensato per aiutarti a decidere prima di acquistare.</p>
      <div class="blog-grid">{''.join(cards)}
      </div>
    </div>
  </section>
"""
    (ROOT / "blog.html").write_text(
        html_page(
            "Blog SitoWeb.info – Guide su siti web, SEO, sicurezza e costi",
            "Guide pratiche per capire costi, sicurezza, hosting gratuito, SEO e scelta del sito web più adatto alla tua attività.",
            "/blog.html",
            main,
            "website",
        ),
        encoding="utf-8",
    )


def build_article_pages(articles: List[Article]) -> None:
    for a in articles:
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": a.title,
            "description": a.description,
            "datePublished": a.date,
            "dateModified": a.updated,
            "author": {"@type": "Person", "name": AUTHOR_NAME},
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "mainEntityOfPage": clean_url(f"/{a.slug}.html"),
        }
        extra_head = f"""
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
</script>
"""
        main = f"""
  <section class="soft-bg">
    <div class="container article-wrap">
      <div class="breadcrumb"><a href="index.html">Home</a> / <a href="blog.html">Blog</a> / {html.escape(a.title)}</div>
      <span class="badge"><i class="{html.escape(a.icon)}"></i> Approfondimento</span>
      <h1>{html.escape(a.title)}</h1>
      <p class="hero-sub">{html.escape(a.description)}</p>
      <p class="article-meta">Pubblicato: {html.escape(a.date)} · Aggiornato: {html.escape(a.updated)}</p>
      <article class="article-content">
        {a.body_html}
        <div class="cta-box">
          <h2>Vuoi capire quale soluzione conviene per la tua attività?</h2>
          <p>Posso aiutarti a scegliere tra sito statico, WordPress, e-commerce o una soluzione più semplice, con costi chiari e senza sorprese.</p>
          <p style="margin-top:20px;"><a class="btn-light" href="index.html#contatti">Richiedi una consulenza gratuita</a></p>
        </div>
      </article>
    </div>
  </section>
"""
        (ROOT / f"{a.slug}.html").write_text(
            html_page(
                f"{a.title} – SitoWeb.info",
                a.description,
                f"/{a.slug}.html",
                main,
                "article",
                extra_head,
            ),
            encoding="utf-8",
        )


def collect_sitemap_entries(articles: List[Article]) -> List[Tuple[str, str, str, str]]:
    today = date.today().isoformat()
    entries: List[Tuple[str, str, str, str]] = []
    seen = set()

    def add_entry(loc: str, lastmod: str, changefreq: str, priority: str) -> None:
        if loc in seen:
            return
        seen.add(loc)
        entries.append((loc, lastmod, changefreq, priority))

    for page in FIXED_PAGES:
        loc = page["loc"]
        target = ROOT / page["file"]
        if page.get("only_if_exists") and not target.exists():
            continue
        add_entry(loc, today, page["changefreq"], page["priority"])

    for a in articles:
        add_entry(f"/{a.slug}.html", a.updated, "monthly", a.priority)

    # Aggiunge anche eventuali pagine articolo .html storiche/non generate da .md.
    skip_names = {"index.html", "blog.html", "privacy-policy.html"}
    for path in sorted(ROOT.glob("*.html")):
        if path.name in skip_names:
            continue
        add_entry(f"/{path.name}", today, "monthly", "0.7")

    return entries


def build_sitemap(articles: List[Article]) -> None:
    urls = []
    for loc, lastmod, changefreq, priority in collect_sitemap_entries(articles):
        urls.append(f"""
  <url>
    <loc>{xml_escape.escape(clean_url(loc))}</loc>
    <lastmod>{xml_escape.escape(lastmod)}</lastmod>
    <changefreq>{xml_escape.escape(changefreq)}</changefreq>
    <priority>{xml_escape.escape(priority)}</priority>
  </url>""")

    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
""" % "".join(urls)

    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def build_robots() -> None:
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def build_rss(articles: List[Article]) -> None:
    now = format_datetime(datetime.now().astimezone())
    items = []

    for a in articles[:20]:
        link = clean_url(f"/{a.slug}.html")
        items.append(f"""
    <item>
      <title>{xml_escape.escape(a.title)}</title>
      <link>{xml_escape.escape(link)}</link>
      <guid>{xml_escape.escape(link)}</guid>
      <description>{xml_escape.escape(a.excerpt)}</description>
      <pubDate>{xml_escape.escape(now)}</pubDate>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{xml_escape.escape(SITE_NAME)}</title>
    <link>{xml_escape.escape(SITE_URL)}</link>
    <description>{xml_escape.escape(SITE_DESCRIPTION)}</description>
    <language>it-IT</language>
    <lastBuildDate>{xml_escape.escape(now)}</lastBuildDate>
{''.join(items)}
  </channel>
</rss>
"""
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")


def main() -> None:
    articles = load_articles()

    build_article_pages(articles)
    build_blog(articles)
    build_sitemap(articles)
    build_robots()
    build_rss(articles)

    print(f"OK: generati/aggiornati {len(articles)} articoli Markdown, blog.html, sitemap.xml, robots.txt e rss.xml.")


if __name__ == "__main__":
    main()
