#!/usr/bin/env python3
"""Generate all 5 article pages following Rafael's premium template.
Combines _gen_article.py parsing + _build_page.py template.
"""
import re, html as html_mod, os, sys
from docx import Document

TEMPLATE_DIR = '/root/unir-platform/apps/web/documentos'
DOCS_DIR = '/root/unir-platform/apps/web/docs/whitepapers'

ARTICLES = [
    {
        'slug': 'manifesto-fundador',
        'docx': 'UNIR_Manifesto_Fundador.docx',
        'title': 'Manifesto Fundador',
        'badge': '⚡ Documento Fundacional',
        'vt_name': 'doc-manifesto',
        'subtitle': 'UNIR — Unidos pela Nacao, Inovacao e Responsabilidade',
        'reading_time': '~12 min',
        'prev': ('portugal-mundo-multipolar', 'Portugal no Mundo Multipolar'),
        'next': ('portugal-90', 'Portugal 90%'),
    },
    {
        'slug': 'portugal-90',
        'docx': 'UNIR_Eixo_I_Portugal_90_Soberania_Defesa_Mar.docx',
        'title': 'Portugal 90%',
        'badge': '⚓ Soberania e Defesa',
        'vt_name': 'doc-soberania',
        'subtitle': 'Dominio Maritimo, Dissuasao e Economia Azul',
        'reading_time': '~18 min',
        'prev': ('manifesto-fundador', 'Manifesto Fundador'),
        'next': ('alternativas-mineracao-marinha', 'Alternativas a Mineracao Marinha'),
    },
    {
        'slug': 'alternativas-mineracao-marinha',
        'docx': 'UNIR_Eixo_I_Anexo_B_Alternativas_Minerais.docx',
        'title': 'Alternativas a Mineracao Marinha',
        'badge': '🔄 Inovacao e Sustentabilidade',
        'vt_name': 'doc-alternativas',
        'subtitle': 'Urban Mining, Biotecnologia e Deep-Sea Tech',
        'reading_time': '~15 min',
        'prev': ('portugal-90', 'Portugal 90%'),
        'next': ('reforma-justica', 'Reforma da Justica e Transparencia'),
    },
    {
        'slug': 'reforma-justica',
        'docx': 'UNIR_Reforma_Justica_Transparencia.docx',
        'title': 'Reforma da Justica e Transparencia',
        'badge': '⚖️ Justica e Transparencia',
        'vt_name': 'doc-justica',
        'subtitle': 'IA nos Tribunais, Combate a Corrupcao',
        'reading_time': '~14 min',
        'prev': ('alternativas-mineracao-marinha', 'Alternativas a Mineracao Marinha'),
        'next': ('justica-digital', 'Justica Digital'),
    },
    {
        'slug': 'justica-digital',
        'docx': 'UNIR_Justica_Digital.docx',
        'title': 'Justica Digital',
        'badge': '🛡️ Identidade Digital',
        'vt_name': 'doc-digital',
        'subtitle': 'Identidade Digital e Responsabilizacao de Plataformas',
        'reading_time': '~10 min',
        'prev': ('reforma-justica', 'Reforma da Justica e Transparencia'),
        'next': None,
    },
]

def slugify(text):
    t = text.lower()
    for c, r in [('ã','a'),('á','a'),('à','a'),('â','a'),('ä','a'),
                 ('é','e'),('è','e'),('ê','e'),('ë','e'),
                 ('í','i'),('ì','i'),('î','i'),('ï','i'),
                 ('ó','o'),('ò','o'),('ô','o'),('ö','o'),('õ','o'),
                 ('ú','u'),('ù','u'),('û','u'),('ü','u'),
                 ('ç','c')]:
        t = t.replace(c, r)
    t = re.sub(r'[^a-z0-9\s-]', '', t)
    t = re.sub(r'\s+', '-', t.strip())
    return t

def extract_sections_html(docx_path):
    """Parse .docx and generate <details> HTML for each top-level section."""
    doc = Document(docx_path)
    raw = []
    for p in doc.paragraphs:
        text = p.text.strip()
        style = p.style.name if p.style else 'None'
        raw.append({'style': style, 'text': text})

    # Build section tree
    sections = []
    stack = [{'level': 0, 'children': sections}]
    heading_counts = {}
    current_content = []

    def flush(target):
        if current_content:
            merged = []
            i = 0
            while i < len(current_content):
                item = current_content[i]
                if item['type'] == 'bullet':
                    bullets = []
                    while i < len(current_content) and current_content[i]['type'] == 'bullet':
                        bullets.append(current_content[i]['text'])
                        i += 1
                    merged.append({'type': 'ul', 'items': bullets})
                else:
                    merged.append(item)
                    i += 1
            target['content'] = merged
            current_content.clear()

    for r in raw:
        text = r['text']
        style = r['style']
        if not text:
            continue
        if style.startswith('Heading'):
            level = int(style.split()[-1])
            anchor = slugify(text)
            if anchor in heading_counts:
                heading_counts[anchor] += 1
                anchor = f"{anchor}-{heading_counts[anchor]}"
            else:
                heading_counts[anchor] = 0
            sec = {'title': text, 'anchor': anchor, 'level': level, 'children': [], 'content': []}
            while stack[-1]['level'] >= level:
                flush(stack[-1])
                stack.pop()
            stack[-1]['children'].append(sec)
            stack.append(sec)
            current_content = sec['content']
        elif style in ('List Bullet', 'List Bullet 2'):
            current_content.append({'type': 'bullet', 'text': text})
        else:
            current_content.append({'type': 'p', 'text': text})

    while len(stack) > 1:
        flush(stack[-1])
        stack.pop()

    # Filter: only top-level sections (level 1), skip UNIR, title, indice
    body_sections = []
    for sec in sections:
        if sec['level'] == 1 and sec['title'] not in ('UNIR', 'Indice', 'Índice'):
            if 'PORTUGAL NO MUNDO' not in sec['title'] and 'PORTUGAL 90%' not in sec['title']:
                body_sections.append(sec)

    # Render
    def render_content(items):
        lines = []
        for item in items:
            if item['type'] == 'p':
                text = html_mod.escape(item['text'])
                lines.append(f'<p>{text}</p>')
            elif item['type'] == 'ul':
                lis = '\n'.join(f'<li>{html_mod.escape(it)}</li>' for it in item['items'])
                lines.append(f'<ul>\n{lis}\n</ul>')
        return '\n'.join(lines)

    def render_section(sec, is_top=True):
        anchor = sec['anchor']
        title = html_mod.escape(sec['title'])
        level = sec['level']
        content = render_content(sec.get('content', []))
        children = ''.join(render_section(c, False) for c in sec.get('children', []))
        if is_top and level == 1:
            return f"""<details class="reader__section" open id="{anchor}">
<summary class="reader__section-title">
{title}
<a href="#{anchor}" class="anchor-link" title="Copiar link da seccao" onclick="copyAnchorLink(event,'{anchor}')">#</a>
</summary>
<div class="reader__section-body">
{content}
{children}
</div>
</details>"""
        elif level == 2:
            return f'<h4 class="reader__subsection" id="{anchor}">{title}</h4>\n{content}\n{children}'
        elif level == 3:
            return f'<h5 class="reader__subsubsection" id="{anchor}">{title}</h5>\n{content}\n{children}'
        return f'{content}\n{children}'

    sections_html = '\n'.join(render_section(s) for s in body_sections)
    toc_items = []
    for s in body_sections:
        toc_items.append({'title': s['title'], 'anchor': s['anchor'], 'level': 1})
        for c in s.get('children', []):
            if c['level'] == 2:
                toc_items.append({'title': c['title'], 'anchor': c['anchor'], 'level': 2})

    return sections_html, toc_items, body_sections

def build_page(article):
    docx_path = os.path.join(DOCS_DIR, article['docx'])
    slug = article['slug']
    out_dir = os.path.join(TEMPLATE_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'index.html')

    print(f'Generating: {slug}...')
    sections_html, toc_items, body_secs = extract_sections_html(docx_path)

    # TOC sidebar
    toc_html = ''
    for item in toc_items:
        cls = 'reader__toc-link--sub' if item['level'] == 2 else ''
        toc_html += f'<li class="{cls}"><a href="#{item["anchor"]}" class="reader__toc-link">{html_mod.escape(item["title"])}</a></li>\n'

    # Prev/next
    prev_slug, prev_title = article['prev'] if article['prev'] else (None, None)
    next_slug, next_title = article['next'] if article['next'] else (None, None)
    prev_html = f'<a href="/documentos/{prev_slug}/" onclick="event.preventDefault();navigateWithTransition(\'/documentos/{prev_slug}/\')">&larr; {prev_title}</a>' if prev_slug else '<a href="#" class="article-prevnext--disabled">&larr; Anterior</a>'
    next_html = f'<a href="/documentos/{next_slug}/" onclick="event.preventDefault();navigateWithTransition(\'/documentos/{next_slug}/\')">{next_title} &rarr;</a>' if next_slug else '<a href="#" class="article-prevnext--disabled">Proximo &rarr;</a>'

    page = f'''<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html_mod.escape(article["title"])} — UNIR</title>
<meta name="description" content="{html_mod.escape(article["subtitle"])}">
<meta property="og:title" content="{html_mod.escape(article["title"])} — UNIR">
<meta property="og:description" content="{html_mod.escape(article["subtitle"])}">
<meta property="og:type" content="article">
<meta name="theme-color" content="#0D47A1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/style.css">
<link rel="stylesheet" href="../../css/reader.css">
<style>
  .article-hero__title {{ view-transition-name: {article["vt_name"]}; }}
  ::view-transition-old({article["vt_name"]}) {{ animation: vt-out 0.2s ease-out forwards; }}
  ::view-transition-new({article["vt_name"]}) {{ animation: vt-in 0.3s ease-out forwards; }}
  @keyframes vt-out {{ to {{ opacity: 0; transform: translateY(-4px); }} }}
  @keyframes vt-in {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav__inner container">
    <a href="/" class="nav__logo">
      <span class="nav__logo-icon">⚡</span>
      <span class="nav__logo-text">UNIR</span>
    </a>
    <div class="nav__links" id="navLinks">
      <a href="/" class="nav__link">Inicio</a>
      <a href="/documentos/" class="nav__link nav__link--cta">Documentos</a>
      <a href="/candidatar/" class="nav__link nav__link--secondary">Integrar</a>
      <button class="theme-toggle" onclick="toggleTheme()" aria-label="Alternar Tema" style="margin-left:8px;">
        <span id="themeIcon">🌙</span> <span id="themeLabel">Modo Escuro</span>
      </button>
    </div>
    <button class="nav__hamburger" id="navToggle" aria-label="Menu">☰</button>
  </div>
</nav>

<div class="article-nav">
  <div class="article-breadcrumb">
    <a href="/">Inicio</a> / <a href="/documentos/">Documentos</a> / <strong>{html_mod.escape(article["title"])}</strong>
  </div>
  <div class="article-actions">
    <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" aria-label="Alternar Tema">
      <span id="themeIcon2">🌙</span> <span id="themeLabel2">Modo Escuro</span>
    </button>
    <button class="share-btn" onclick="shareArticle()" aria-label="Partilhar">🔗 Partilhar</button>
  </div>
</div>

<div class="reader__progress" id="progressBar"><div class="reader__progress-fill" id="progressFill"></div></div>

<article class="reader">

<aside class="reader__sidebar">
  <button class="reader__toc-toggle" id="tocToggle" aria-expanded="false">Indice do Documento</button>
  <nav class="reader__toc" id="tocNav">
    <h4 class="reader__toc-title">Indice de Conteudos</h4>
    <ol>
{toc_html}
    </ol>
  </nav>
</aside>

<div class="reader__body">

<a href="/documentos/" class="reader__back" onclick="event.preventDefault();navigateWithTransition('/documentos/');">&larr; Voltar aos Documentos</a>

<header class="article-hero">
  <span class="article-hero__badge">{article["badge"]}</span>
  <h1 class="article-hero__title">{html_mod.escape(article["title"])}</h1>
  <p class="article-hero__subtitle">{html_mod.escape(article["subtitle"])}</p>
  <div class="article-hero__meta">
    <span class="article-hero__meta-item">⏱️ {article["reading_time"]} de leitura</span>
    <span class="article-hero__meta-dot"></span>
    <span class="article-hero__meta-item">🏛️ Movimento UNIR</span>
  </div>
</header>

<div class="reader__content">
{sections_html}
</div>

<footer class="reader__footer">
  <p>Documento Estrategico &middot; UNIR &mdash; Unidos pela Nacao, Inovacao e Responsabilidade</p>
</footer>

</div>
</article>

<div class="article-prevnext">
  {prev_html}
  {next_html}
</div>

<footer class="footer">
  <div class="container footer__inner">
    <div class="footer__brand">
      <span class="nav__logo-text">UNIR</span>
      <p class="footer__tagline">Um partido feito por pessoas. Para pessoas.</p>
    </div>
    <div class="footer__links">
      <a href="/" class="footer__link">Inicio</a>
      <a href="/documentos/" class="footer__link">Documentos</a>
      <a href="/candidatar/" class="footer__link">Integrar</a>
    </div>
    <p class="footer__copy">Feito em Portugal. Por cidadaos. Para cidadaos.</p>
  </div>
</footer>

<div id="toast" class="toast-notification">Link copiado!</div>

<script>
(function(){{
  var b=window.location.pathname.replace(/\\/[^/]*\\/?$/,'').replace(/\\/[^/]*\\/?$/,'');
  document.querySelectorAll('a[href^="/"]').forEach(function(l){{
    var h=l.getAttribute('href');
    if(h.startsWith('//')||h.startsWith('http')||h.startsWith('/#'))return;
    if(h==='/'){{l.setAttribute('href',b+'/');return}}
    if(h.startsWith('/documentos')){{l.setAttribute('href',b+'/documentos/');return}}
    if(h.startsWith('/candidatar')){{l.setAttribute('href',b+'/candidatar/');return}}
  }});
}})();

function initTheme(){{
  var t=localStorage.getItem('unir_theme');
  var d=window.matchMedia('(prefers-color-scheme:dark)').matches;
  if(t==='dark'||(!t&&d)){{document.documentElement.setAttribute('data-theme','dark');updateUI(true);}}
  else{{document.documentElement.removeAttribute('data-theme');updateUI(false);}}
}}
function toggleTheme(){{
  var is=document.documentElement.getAttribute('data-theme')==='dark';
  if(is){{document.documentElement.removeAttribute('data-theme');localStorage.setItem('unir_theme','light');updateUI(false);}}
  else{{document.documentElement.setAttribute('data-theme','dark');localStorage.setItem('unir_theme','dark');updateUI(true);}}
}}
function updateUI(dark){{
  var icons=document.querySelectorAll('#themeIcon,#themeIcon2');
  var labels=document.querySelectorAll('#themeLabel,#themeLabel2');
  icons.forEach(function(i){{i.textContent=dark?'☀️':'🌙';}});
  labels.forEach(function(l){{l.textContent=dark?'Modo Claro':'Modo Escuro';}});
}}
initTheme();

function copyAnchorLink(e,id){{
  e.preventDefault();e.stopPropagation();
  var url=window.location.origin+window.location.pathname+'#'+id;
  navigator.clipboard.writeText(url).then(function(){{showToast('Link da seccao copiado!');history.pushState(null,null,'#'+id);}})
    .catch(function(){{showToast('Erro ao copiar link');}});
}}
function shareArticle(){{
  if(navigator.share){{navigator.share({{title:document.title,url:window.location.href}}).catch(function(){{}});}}
  else{{navigator.clipboard.writeText(window.location.href).then(function(){{showToast('Link copiado!');}});}}
}}
function navigateWithTransition(url){{
  if(document.startViewTransition){{document.startViewTransition(function(){{window.location.href=url;}});}}
  else{{window.location.href=url;}}
}}
function showToast(msg){{
  var t=document.getElementById('toast');if(!t)return;
  t.textContent=msg;t.classList.add('toast-notification--show');
  setTimeout(function(){{t.classList.remove('toast-notification--show');}},2600);
}}

(function(){{
  var bar=document.getElementById('progressFill');
  if(bar){{window.addEventListener('scroll',function(){{var h=document.documentElement;
    var pct=(h.scrollTop/(h.scrollHeight-h.clientHeight))*100;
    bar.style.width=Math.min(100,Math.max(0,pct))+'%';}});}}
  var tocLinks=document.querySelectorAll('.reader__toc-link');
  var headings=document.querySelectorAll('.reader__section[id]');
  if(headings.length){{
    var obs=new IntersectionObserver(function(entries){{entries.forEach(function(e){{
      if(e.isIntersecting){{tocLinks.forEach(function(l){{l.classList.remove('reader__toc-link--active');}});
      var link=document.querySelector('.reader__toc-link[href="#'+e.target.id+'"]');
      if(link)link.classList.add('reader__toc-link--active');}}
    }});}},{{rootMargin:'-10% 0px -70% 0px'}});
    headings.forEach(function(h){{obs.observe(h);}});
  }}
  var tt=document.getElementById('tocToggle'),tn=document.getElementById('tocNav');
  if(tt&&tn){{tt.addEventListener('click',function(){{
    var o=!tn.classList.contains('reader__toc--open');
    tn.classList.toggle('reader__toc--open',o);
    tt.classList.toggle('reader__toc-toggle--open',o);
    tt.setAttribute('aria-expanded',o?'true':'false');
  }});}}
  var nt=document.getElementById('navToggle'),nl=document.getElementById('navLinks');
  if(nt&&nl){{nt.addEventListener('click',function(){{nl.classList.toggle('nav__links--open');}});}}
}})();
</script>

</body>
</html>'''

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page)

    sec_count = sections_html.count('<details class=')
    print(f'  -> {out_path} ({len(page)} bytes, {sec_count} sections, {len(toc_items)} toc items)')

# ── Run ──
for article in ARTICLES:
    try:
        build_page(article)
    except Exception as e:
        print(f'  ERROR: {e}')

print('\nDone! 5 pages generated.')
