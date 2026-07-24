#!/usr/bin/env python3
"""Build article page from template + generated body."""
import re, sys

# Config — adjust per article
SLUG = 'portugal-mundo-multipolar'
VT_NAME = 'doc-multipolar'
TITLE = 'Portugal no Mundo Multipolar'
PREV_SLUG = None          # None = disabled
NEXT_SLUG = 'manifesto-fundador'
NEXT_TITLE = 'Manifesto Fundador'

# Load generated article body
with open('/root/unir-platform/apps/web/docs/whitepapers/WHITEPAPER_PORTUGAL_MUNDO_MULTIPOLAR_UNIR.html') as f:
    gen = f.read()

m = re.search(r'(<details class="reader__section".*</details>)', gen, re.DOTALL)
if not m:
    print("ERROR: Could not find article body")
    sys.exit(1)
body = m.group(1)

# Build prev/next HTML
prev_html = f'<a href="#" class="article-prevnext--disabled">&larr; Anterior</a>'
if PREV_SLUG:
    prev_html = f'<a href="/documentos/{PREV_SLUG}/">&larr; Anterior</a>'

next_html = f'<a href="#" class="article-prevnext--disabled">Proximo &rarr;</a>'
if NEXT_SLUG:
    next_html = f'<a href="/documentos/{NEXT_SLUG}/">Proximo: {NEXT_TITLE} &rarr;</a>'

page = f'''<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{TITLE} — UNIR</title>
<meta name="description" content="Documento estrategico do UNIR. Conhece as propostas e o programa.">
<meta property="og:title" content="{TITLE} — UNIR">
<meta property="og:description" content="Documento estrategico do partido UNIR.">
<meta property="og:type" content="article">
<meta name="theme-color" content="#0D47A1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/style.css" id="mainStylesheet">
<link rel="stylesheet" href="../../css/reader.css" id="readerStylesheet">
<script>
(function(){{var b=window.location.pathname.replace(/\\/[^/]*\\/?$/,'').replace(/\\/[^/]*\\/?$/,'');
var s=document.getElementById('mainStylesheet');if(s)s.href=b+'/css/style.css';
var r=document.getElementById('readerStylesheet');if(r)r.href=b+'/css/reader.css';
}})();
</script>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='28' font-size='28'>⚡</text></svg>">
<style>
  /* ── View Transition: morph article title between pages ── */
  .reader__title {{ view-transition-name: {VT_NAME}; }}
  ::view-transition-old({VT_NAME}) {{ animation: vt-out 0.2s ease-out forwards; }}
  ::view-transition-new({VT_NAME}) {{ animation: vt-in 0.3s ease-out forwards; }}
  @keyframes vt-out {{ to {{ opacity: 0; transform: translateY(-4px); }} }}
  @keyframes vt-in {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}

  /* Smoother cross-fade for the rest of the page */
  ::view-transition-old(root) {{ animation: vt-page-out 0.15s ease-out forwards; }}
  ::view-transition-new(root) {{ animation: vt-page-in 0.25s ease-out forwards; }}
  @keyframes vt-page-out {{ to {{ opacity: 0.4; }} }}
  @keyframes vt-page-in {{ from {{ opacity: 0.6; }} to {{ opacity: 1; }} }}

  /* Breadcrumb */
  .article-nav {{ max-width:1100px; margin:0 auto; padding:24px 32px 0; }}
  .article-breadcrumb {{ font-size:0.82rem; color:#9E9E9E; margin-bottom:4px; }}
  .article-breadcrumb a {{ color:#0D47A1; text-decoration:none; }}
  .article-breadcrumb a:hover {{ text-decoration:underline; }}

  @media(max-width:900px){{ .article-nav {{ padding-left:16px; padding-right:16px; }} }}
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
    </div>
    <button class="nav__hamburger" id="navToggle" aria-label="Menu">&#9776;</button>
  </div>
</nav>

<div class="article-nav">
  <div class="article-breadcrumb">
    <a href="/">Inicio</a> / <a href="/documentos/">Documentos</a> / <strong>{TITLE}</strong>
  </div>
</div>

<div class="reader__progress" id="progressBar"><div class="reader__progress-fill" id="progressFill"></div></div>

<article class="reader">

<aside class="reader__sidebar">
  <button class="reader__toc-toggle" id="tocToggle" aria-expanded="false">Indice</button>
  <nav class="reader__toc" id="tocNav">
    <h4 class="reader__toc-title">Indice</h4>
    <ol>
<li><a href="#1-resumo-executivo" class="reader__toc-link">1. Resumo Executivo</a></li>
<li><a href="#2-contexto-geopolitico-o-fim-do-unipolarismo" class="reader__toc-link">2. Contexto Geopolitico</a></li>
<li><a href="#3-portugal-na-encruzilhada-dependencias-e-oportunidades" class="reader__toc-link">3. Portugal na Encruzilhada</a></li>
<li><a href="#4-pilar-i---reducao-da-dependencia-estrategica-dos-eua" class="reader__toc-link">4. Pilar I — Reducao Dep. EUA</a></li>
<li class="reader__toc-link--sub"><a href="#41-defesa-e-soberania-militar" class="reader__toc-link">4.1. Defesa</a></li>
<li class="reader__toc-link--sub"><a href="#42-tecnologia-e-infraestrutura-digital" class="reader__toc-link">4.2. Tecnologia</a></li>
<li class="reader__toc-link--sub"><a href="#43-diplomacia-e-alinhamento" class="reader__toc-link">4.3. Diplomacia</a></li>
<li><a href="#5-pilar-ii---parceria-estrategica-com-a-china" class="reader__toc-link">5. Pilar II — China</a></li>
<li class="reader__toc-link--sub"><a href="#51-oportunidades" class="reader__toc-link">5.1. Oportunidades</a></li>
<li class="reader__toc-link--sub"><a href="#52-salvaguardas-obrigatorias" class="reader__toc-link">5.2. Salvaguardas</a></li>
<li class="reader__toc-link--sub"><a href="#53-areas-prioritarias-para-cooperacao" class="reader__toc-link">5.3. Areas Prioritarias</a></li>
<li><a href="#6-pilar-iii---brasil-como-socio-preferencial" class="reader__toc-link">6. Pilar III — Brasil</a></li>
<li><a href="#7-pilar-iv---palops-e-a-lusofonia" class="reader__toc-link">7. Pilar IV — PALOPs</a></li>
<li><a href="#8-pilar-v---africa-como-proximo-horizonte" class="reader__toc-link">8. Pilar V — Africa</a></li>
<li><a href="#9-eixo-transversal---tecnologia-e-estado-inteligente" class="reader__toc-link">9. Eixo Transversal</a></li>
<li><a href="#10-plano-de-implementacao-2026-2035" class="reader__toc-link">10. Plano Implementacao</a></li>
<li><a href="#11-analise-de-riscos-e-mitigacao" class="reader__toc-link">11. Analise Riscos</a></li>
<li><a href="#12-conclusao-e-proximos-passos" class="reader__toc-link">12. Conclusao</a></li>
    </ol>
  </nav>
</aside>

<div class="reader__body">

<a href="/documentos/" class="reader__back">&larr; Voltar aos Documentos</a>

<header class="reader__header">
<h1 class="reader__title">{TITLE.upper()}</h1>
</header>

<div class="reader__content">
{body}
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

<script>
(function(){{var b=window.location.pathname.replace(/\\/[^/]*\\/?$/,'').replace(/\\/[^/]*\\/?$/,'');
document.querySelectorAll('a[href^="/"]').forEach(function(l){{
var h=l.getAttribute('href');if(h.startsWith('//')||h.startsWith('http')||h.startsWith('/#'))return;
if(h==='/'){{l.setAttribute('href',b+'/');return}}
if(h.startsWith('/documentos')){{l.setAttribute('href',b+'/documentos/');return}}
if(h.startsWith('/candidatar')){{l.setAttribute('href',b+'/candidatar/');return}}
}});
}})();
</script>

<script>
(function(){{
  // Progress bar
  var bar=document.getElementById('progressFill');
  if(bar){{window.addEventListener('scroll',function(){{var h=document.documentElement;
    var pct=(h.scrollTop/(h.scrollHeight-h.clientHeight))*100;
    bar.style.width=Math.min(100,Math.max(0,pct))+'%';}});}}

  // TOC IntersectionObserver
  var tocLinks=document.querySelectorAll('.reader__toc-link');
  var headings=document.querySelectorAll('.reader__section[id],.reader__subsection[id]');
  if(headings.length){{
    var observer=new IntersectionObserver(function(entries){{entries.forEach(function(e){{
      if(e.isIntersecting){{tocLinks.forEach(function(l){{l.classList.remove('reader__toc-link--active');}});
      var link=document.querySelector('.reader__toc-link[href="#'+e.target.id+'"]');
      if(link)link.classList.add('reader__toc-link--active');}}
    }});}},{{rootMargin:'-10% 0px -75% 0px'}});
    headings.forEach(function(h){{observer.observe(h);}});
  }}

  // Mobile TOC toggle
  var tocToggle=document.getElementById('tocToggle');
  var tocNav=document.getElementById('tocNav');
  if(tocToggle&&tocNav){{
    tocToggle.addEventListener('click',function(){{
      var open=!tocNav.classList.contains('reader__toc--open');
      tocNav.classList.toggle('reader__toc--open',open);
      tocToggle.classList.toggle('reader__toc-toggle--open',open);
      tocToggle.setAttribute('aria-expanded',open?'true':'false');
    }});
  }}

  // Hamburger menu
  document.getElementById('navToggle').addEventListener('click',function(){{
    document.getElementById('navLinks').classList.toggle('nav__links--open');}});
  document.querySelectorAll('.nav__link').forEach(function(l){{
    l.addEventListener('click',function(){{document.getElementById('navLinks').classList.remove('nav__links--open');}});}});
}})();
</script>

</body>
</html>'''

out = '/root/unir-platform/apps/web/documentos/portugal-mundo-multipolar/index.html'
with open(out, 'w') as f:
    f.write(page)

print(f'Page: {len(page)} chars, {page.count("<details class=")} sections, {page.count("<table class=")} tables')
print(f'Written: {out}')
