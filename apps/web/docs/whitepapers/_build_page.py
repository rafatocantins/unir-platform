#!/usr/bin/env python3
"""Build article page from template + generated body."""
import re

# Load generated article body
with open('/root/unir-platform/apps/web/docs/whitepapers/WHITEPAPER_PORTUGAL_MUNDO_MULTIPOLAR_UNIR.html') as f:
    gen = f.read()

m = re.search(r'(<details class="reader__section".*</details>)', gen, re.DOTALL)
body = m.group(1)

# Load site template parts
nav = '''<nav class="nav">
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
</nav>'''

footer = '''<footer class="footer">
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
</footer>'''

page = f'''<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Portugal no Mundo Multipolar — UNIR</title>
<meta name="description" content="Estrategia Lusofona e Tecnologica 2035. Reposicionamento de Portugal como hub geopolitico no mundo multipolar.">
<meta property="og:title" content="Portugal no Mundo Multipolar — UNIR">
<meta property="og:description" content="5 pilares para Portugal 2035: soberania, lusofonia, tecnologia e Estado Inteligente.">
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
  .reader__header {{ view-transition-name: doc-multipolar; }}
  ::view-transition-old(doc-multipolar) {{ animation: vt-fade-out 0.25s ease-out forwards; }}
  ::view-transition-new(doc-multipolar) {{ animation: vt-fade-in 0.35s ease-out forwards; }}
  @keyframes vt-fade-out {{ to {{ opacity: 0; transform: scale(0.97); }} }}
  @keyframes vt-fade-in {{ from {{ opacity: 0; transform: scale(1.03); }} to {{ opacity: 1; transform: scale(1); }} }}

  .article-nav {{ max-width:1100px; margin:0 auto; padding:16px 32px 0; }}
  .article-breadcrumb {{ font-size:0.82rem; color:#9E9E9E; margin-bottom:8px; }}
  .article-breadcrumb a {{ color:#0D47A1; text-decoration:none; }}
  .article-breadcrumb a:hover {{ text-decoration:underline; }}
  .article-prevnext {{ display:flex; justify-content:space-between; max-width:1100px; margin:60px auto 40px; padding:0 32px; gap:16px; }}
  .article-prevnext a {{ display:flex; align-items:center; gap:8px; padding:14px 20px; border-radius:10px; background:#F5F7FA; color:#0D47A1; text-decoration:none; font-weight:600; font-size:0.9rem; transition:background 0.2s; }}
  .article-prevnext a:hover {{ background:#E3F2FD; }}
  .article-prevnext a.article-prevnext--disabled {{ color:#BDBDBD; pointer-events:none; }}
  @media(max-width:900px){{ .article-nav,.article-prevnext {{ padding-left:16px; padding-right:16px; }} .article-prevnext {{ flex-direction:column; }} }}
</style>
</head>
<body>

{nav}

<div class="article-nav">
  <div class="article-breadcrumb">
    <a href="/">Inicio</a> / <a href="/documentos/">Documentos</a> / <strong>Portugal no Mundo Multipolar</strong>
  </div>
</div>

<div class="reader__progress" id="progressBar"><div class="reader__progress-fill" id="progressFill"></div></div>

<article class="reader">

<aside class="reader__sidebar">
  <nav class="reader__toc">
    <h4 class="reader__toc-title">Indice</h4>
    <ol>
<li><a href="#1-resumo-executivo" class="reader__toc-link">1. Resumo Executivo</a></li>
<li><a href="#2-contexto-geopolitico-o-fim-do-unipolarismo" class="reader__toc-link">2. Contexto Geopolitico: O Fim do Unipolarismo</a></li>
<li><a href="#3-portugal-na-encruzilhada-dependencias-e-oportunidades" class="reader__toc-link">3. Portugal na Encruzilhada</a></li>
<li><a href="#4-pilar-i---reducao-da-dependencia-estrategica-dos-eua" class="reader__toc-link">4. Pilar I — Reducao da Dependencia dos EUA</a></li>
<li class="reader__toc-link--sub"><a href="#41-defesa-e-soberania-militar" class="reader__toc-link">4.1. Defesa e Soberania Militar</a></li>
<li class="reader__toc-link--sub"><a href="#42-tecnologia-e-infraestrutura-digital" class="reader__toc-link">4.2. Tecnologia e Infraestrutura Digital</a></li>
<li class="reader__toc-link--sub"><a href="#43-diplomacia-e-alinhamento" class="reader__toc-link">4.3. Diplomacia e Alinhamento</a></li>
<li><a href="#5-pilar-ii---parceria-estrategica-com-a-china" class="reader__toc-link">5. Pilar II — Parceria com a China</a></li>
<li class="reader__toc-link--sub"><a href="#51-oportunidades" class="reader__toc-link">5.1. Oportunidades</a></li>
<li class="reader__toc-link--sub"><a href="#52-salvaguardas-obrigatorias" class="reader__toc-link">5.2. Salvaguardas Obrigatorias</a></li>
<li class="reader__toc-link--sub"><a href="#53-areas-prioritarias-para-cooperacao" class="reader__toc-link">5.3. Areas Prioritarias</a></li>
<li><a href="#6-pilar-iii---brasil-como-socio-preferencial" class="reader__toc-link">6. Pilar III — Brasil como Socio Preferencial</a></li>
<li><a href="#7-pilar-iv---palops-e-a-lusofonia" class="reader__toc-link">7. Pilar IV — PALOPs e a Lusofonia</a></li>
<li><a href="#8-pilar-v---africa-como-proximo-horizonte" class="reader__toc-link">8. Pilar V — Africa</a></li>
<li><a href="#9-eixo-transversal---tecnologia-e-estado-inteligente" class="reader__toc-link">9. Eixo Transversal — Tecnologia</a></li>
<li><a href="#10-plano-de-implementacao-2026-2035" class="reader__toc-link">10. Plano de Implementacao</a></li>
<li><a href="#11-analise-de-riscos-e-mitigacao" class="reader__toc-link">11. Analise de Riscos</a></li>
<li><a href="#12-conclusao-e-proximos-passos" class="reader__toc-link">12. Conclusao</a></li>
    </ol>
  </nav>
</aside>

<div class="reader__body">

<header class="reader__header">
<h1 class="reader__title">PORTUGAL NO MUNDO MULTIPOLAR</h1>
</header>

<div class="reader__content">
{body}
</div>

<footer class="reader__footer">
  <p>Documento Estrategico &middot; UNIR &mdash; Unidos pela Nacao, Inovacao e Responsabilidade</p>
  <p>Maio 2026 &middot; Classificacao: Publico</p>
</footer>

</div>
</article>

<div class="article-prevnext">
  <a href="#" class="article-prevnext--disabled">&larr; Anterior</a>
  <a href="/documentos/manifesto-fundador/">Proximo: Manifesto Fundador &rarr;</a>
</div>

{footer}

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
  var bar=document.getElementById('progressFill');
  if(bar){{window.addEventListener('scroll',function(){{var h=document.documentElement;
    var pct=(h.scrollTop/(h.scrollHeight-h.clientHeight))*100;
    bar.style.width=Math.min(100,Math.max(0,pct))+'%';}});}}
  var tocLinks=document.querySelectorAll('.reader__toc-link');
  var headings=document.querySelectorAll('.reader__section[id],.reader__subsection[id]');
  if(!headings.length)return;
  var observer=new IntersectionObserver(function(entries){{entries.forEach(function(e){{
    if(e.isIntersecting){{tocLinks.forEach(function(l){{l.classList.remove('reader__toc-link--active');}});
    var link=document.querySelector('.reader__toc-link[href="#'+e.target.id+'"]');
    if(link)link.classList.add('reader__toc-link--active');}}
  }});}},{{rootMargin:'-10% 0px -75% 0px'}});
  headings.forEach(function(h){{observer.observe(h);}});

  document.getElementById('navToggle').addEventListener('click',function(){{
    document.getElementById('navLinks').classList.toggle('nav__links--open');}});
  document.querySelectorAll('.nav__link').forEach(function(l){{
    l.addEventListener('click',function(){{document.getElementById('navLinks').classList.remove('nav__links--open');}});}});
}})();
</script>

</body>
</html>'''

with open('/root/unir-platform/apps/web/documentos/portugal-mundo-multipolar/index.html', 'w') as f:
    f.write(page)

print(f'Page: {len(page)} chars, {page.count("<details class=")} sections, {page.count("<table class=")} tables')
