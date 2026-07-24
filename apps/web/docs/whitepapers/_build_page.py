import sys
import html as html_mod
import docx

# Arguments: input.docx output.html title vt_name prev_slug prev_title next_slug next_title
DOCX_PATH = sys.argv[1]
OUT = sys.argv[2]
TITLE = sys.argv[3]
VT_NAME = sys.argv[4] if len(sys.argv) > 4 else 'doc-title'
PREV_SLUG = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != 'NONE' else None
PREV_TITLE = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != 'NONE' else ''
NEXT_SLUG = sys.argv[7] if len(sys.argv) > 7 and sys.argv[7] != 'NONE' else None
NEXT_TITLE = sys.argv[8] if len(sys.argv) > 8 and sys.argv[8] != 'NONE' else ''

doc = docx.Document(DOCX_PATH)

def make_anchor(text):
    text = text.lower()
    for c in ['ã','á','à','â','ä']: text = text.replace(c, 'a')
    for c in ['é','è','ê','ë']: text = text.replace(c, 'e')
    for c in ['í','ì','î','ï']: text = text.replace(c, 'i')
    for c in ['ó','ò','ô','ö','õ']: text = text.replace(c, 'o')
    for c in ['ú','ù','û','ü']: text = text.replace(c, 'u')
    text = text.replace('ç', 'c')
    import re
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text

prev_html = f'<a href="/documentos/{PREV_SLUG}/">&larr; {PREV_TITLE}</a>' if PREV_SLUG else '<a href="#" class="article-prevnext--disabled">&larr; Anterior</a>'
next_html = f'<a href="/documentos/{NEXT_SLUG}/">{NEXT_TITLE} &rarr;</a>' if NEXT_SLUG else '<a href="#" class="article-prevnext--disabled">Proximo &rarr;</a>'

page = f'''<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html_mod.escape(TITLE)} — UNIR</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/style.css">
<link rel="stylesheet" href="../../css/reader.css">
<style>
  .article-hero__title {{ view-transition-name: {VT_NAME}; }}
  ::view-transition-old({VT_NAME}) {{ animation: vt-out 0.2s ease-out forwards; }}
  ::view-transition-new({VT_NAME}) {{ animation: vt-in 0.3s ease-out forwards; }}
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
    </div>
    <button class="nav__hamburger" id="navToggle" aria-label="Menu de Navegacao">&#9776;</button>
  </div>
</nav>

<div class="article-nav">
  <div class="article-breadcrumb">
    <a href="/">Inicio</a> / <a href="/documentos/">Documentos</a> / <strong>{html_mod.escape(TITLE)}</strong>
  </div>
  <div class="article-actions">
    <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" aria-label="Alternar Tema Claro / Escuro">
      <span id="themeIcon">🌙</span> <span id="themeLabel">Modo Escuro</span>
    </button>
    <button class="share-btn" onclick="shareArticle()" aria-label="Partilhar este artigo">
      🔗 Partilhar
    </button>
  </div>
</div>

<div class="reader__progress" id="progressBar"><div class="reader__progress-fill" id="progressFill"></div></div>

<article class="reader">

<aside class="reader__sidebar">
  <button class="reader__toc-toggle" id="tocToggle" aria-expanded="false">Indice</button>
  <nav class="reader__toc" id="tocNav">
    <h4 class="reader__toc-title">Indice</h4>
    <ol id="tocList"></ol>
  </nav>
</aside>

<div class="reader__body">

<a href="/documentos/" class="reader__back">&larr; Voltar aos Documentos</a>

<header class="article-hero">
  <span class="article-hero__badge">⚡ Documento Oficial UNIR</span>
  <h1 class="article-hero__title">{html_mod.escape(TITLE)}</h1>
  <div class="article-hero__meta">
    <span class="article-hero__meta-item">⏱️ ~15 min de leitura</span>
    <span class="article-hero__meta-dot"></span>
    <span class="article-hero__meta-item">🏛️ Movimento UNIR</span>
  </div>
</header>

<div class="reader__content" id="readerContent">
  <!-- Dynamic DOCX content rendered here -->
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

<div id="toast" class="toast-notification">Link copiado para a area de transferencia!</div>

<script>
(function(){{
  var b = window.location.pathname.replace(/\\/[^/]*\\/?$/, '').replace(/\\/[^/]*\\/?$/, '');
  document.querySelectorAll('a[href^="/"]').forEach(function(l){{
    var h = l.getAttribute('href');
    if (h.startsWith('//') || h.startsWith('http') || h.startsWith('/#')) return;
    if (h === '/') {{ l.setAttribute('href', b + '/'); return; }}
    if (h.startsWith('/documentos')) {{ l.setAttribute('href', b + '/documentos/'); return; }}
    if (h.startsWith('/candidatar')) {{ l.setAttribute('href', b + '/candidatar/'); return; }}
  }});
}})();

function initTheme() {{
  var savedTheme = localStorage.getItem('unir_theme');
  var systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {{
    document.documentElement.setAttribute('data-theme', 'dark');
    updateThemeUI(true);
  }} else {{
    document.documentElement.removeAttribute('data-theme');
    updateThemeUI(false);
  }}
}}

function toggleTheme() {{
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  if (isDark) {{
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('unir_theme', 'light');
    updateThemeUI(false);
  }} else {{
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('unir_theme', 'dark');
    updateThemeUI(true);
  }}
}}

function updateThemeUI(isDark) {{
  var icon = document.getElementById('themeIcon');
  var label = document.getElementById('themeLabel');
  if (icon && label) {{
    icon.textContent = isDark ? '☀️' : '🌙';
    label.textContent = isDark ? 'Modo Claro' : 'Modo Escuro';
  }}
}}
initTheme();

function copyAnchorLink(event, id) {{
  event.preventDefault();
  event.stopPropagation();
  var url = window.location.origin + window.location.pathname + '#' + id;
  navigator.clipboard.writeText(url).then(function() {{
    showToast('Link da seccao copiado!');
    history.pushState(null, null, '#' + id);
  }}).catch(function() {{
    showToast('Erro ao copiar link');
  }});
}}

function shareArticle() {{
  if (navigator.share) {{
    navigator.share({{
      title: document.title,
      url: window.location.href
    }}).catch(function(){{}});
  }} else {{
    navigator.clipboard.writeText(window.location.href).then(function(){{
      showToast('Link do artigo copiado!');
    }});
  }}
}}

function showToast(msg) {{
  var toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('toast-notification--show');
  setTimeout(function() {{
    toast.classList.remove('toast-notification--show');
  }}, 2600);
}}

(function(){{
  var bar = document.getElementById('progressFill');
  if (bar) {{
    window.addEventListener('scroll', function() {{
      var h = document.documentElement;
      var pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
    }});
  }}
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  if (navToggle && navLinks) {{
    navToggle.addEventListener('click', function() {{
      navLinks.classList.toggle('nav__links--open');
    }});
  }}
}})();
</script>

</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(page)

print(f"Page written: {OUT}")
