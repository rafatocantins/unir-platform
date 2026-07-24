#!/usr/bin/env python3
"""Generate reader-style article HTML from .docx — with topic detection + pillar lists."""
from docx import Document
import re, html as html_mod, unicodedata

DOC = '/root/unir-platform/apps/web/docs/whitepapers/WHITEPAPER_PORTUGAL_MUNDO_MULTIPOLAR_UNIR.docx'
OUT_HTML = '/root/unir-platform/apps/web/docs/whitepapers/WHITEPAPER_PORTUGAL_MUNDO_MULTIPOLAR_UNIR.html'

doc = Document(DOC)

def slugify(text):
    t = text.lower()
    t = unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode()
    t = re.sub(r'[^a-z0-9\s-]', '', t)
    t = re.sub(r'\s+', '-', t.strip())
    return t

# ── Parse docx ──
raw = []
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    style = p.style.name if p.style else 'None'
    raw.append({'idx': i, 'style': style, 'text': text})

sections = []
stack = [{'level': 0, 'children': sections}]
heading_counts = {}
current_content = []

def flush_content(target):
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
        target['content_before_children'] = merged
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
        sec = {'title': text, 'anchor': anchor, 'level': level,
               'children': [], 'content_before_children': []}
        while stack[-1]['level'] >= level:
            flush_content(stack[-1])
            stack.pop()
        parent = stack[-1]
        parent['children'].append(sec)
        stack.append(sec)
        current_content = sec['content_before_children']
    elif style in ('List Bullet', 'List Bullet 2'):
        current_content.append({'type': 'bullet', 'text': text})
    else:
        current_content.append({'type': 'p', 'text': text})

while len(stack) > 1:
    flush_content(stack[-1])
    stack.pop()
flush_content(stack[0])

root_content = stack[0].get('content_before_children', [])
body_sections = []
for sec in sections:
    if sec['level'] == 1 and sec['title'] not in ('UNIR', 'PORTUGAL NO MUNDO MULTIPOLAR',
                                                    'Indice', 'Índice'):
        body_sections.append(sec)

# ── Tables ──
tables_data = []
for table in doc.tables:
    rows = [[c.text.strip() for c in row.cells] for row in table.rows]
    tables_data.append(rows)

TABLE_PLACEMENT = {
    0: '2-contexto-geopolitico-o-fim-do-unipolarismo',
    1: 'dependencias-atuais',
    2: 'oportunidades-inexploradas',
    3: '51-oportunidades',
    4: '82-vantagem-competitiva-portuguesa',
    5: 'fase-1-2026-2028---fundacao',
    6: 'fase-2-2029-2032---expansao',
    7: 'fase-3-2033-2035---consolidacao',
    8: '11-analise-de-riscos-e-mitigacao',
}

# ── Topic / Pillar detection ──

def is_topic(text):
    """Short phrase that should be visually highlighted (bold, colored)."""
    t = text.strip()
    if len(t) > 80:
        return False
    if t.endswith(':'):
        return True
    if len(t) <= 50 and not re.search(r'[.!?]$', t):
        return True
    return False

def is_pillar_item(text):
    """'Term: description' pattern — convert to styled list item."""
    t = text.strip()
    if ':' not in t:
        return None
    parts = t.split(':', 1)
    term = parts[0].strip()
    desc = parts[1].strip() if len(parts) > 1 else ''
    if len(term) > 60:
        return None
    if len(desc) < 3:
        return None
    return (term, desc)

def merge_pillar_lists(items):
    """Group consecutive p elements that are pillar items into pillar_list blocks."""
    result = []
    i = 0
    while i < len(items):
        item = items[i]
        if item.get('type') != 'p':
            result.append(item)
            i += 1
            continue
        pillar_items = []
        j = i
        while j < len(items) and items[j].get('type') == 'p':
            match = is_pillar_item(items[j].get('text', ''))
            if match:
                pillar_items.append(match)
                j += 1
            else:
                break
        if len(pillar_items) >= 2:
            result.append({'type': 'pillar_list', 'items': pillar_items})
            i = j
        else:
            result.append(item)
            i += 1
    return result

# ── Render ──

def render_table(rows):
    if not rows:
        return ''
    html_rows = ''
    for ri, row in enumerate(rows):
        tag = 'th' if ri == 0 else 'td'
        cells = ''.join(f'<{tag}>{html_mod.escape(c)}</{tag}>' for c in row)
        html_rows += f'<tr>{cells}</tr>\n'
    return f'<table class="reader__table">\n{html_rows}</table>'

def render_content(items, section_anchor=''):
    items = merge_pillar_lists(items)
    lines = []
    for item in items:
        if item['type'] == 'p':
            text = html_mod.escape(item['text'])
            cls = ' class="reader__topic"' if is_topic(item['text']) else ''
            lines.append(f'<p{cls}>{text}</p>')
        elif item['type'] == 'ul':
            lis = '\n'.join(f'<li>{html_mod.escape(it)}</li>' for it in item['items'])
            lines.append(f'<ul>\n{lis}\n</ul>')
        elif item['type'] == 'pillar_list':
            lis = ''
            for term, desc in item['items']:
                lis += f'<li><strong>{html_mod.escape(term)}:</strong> {html_mod.escape(desc)}</li>\n'
            lines.append(f'<ul class="reader__pillar-list">\n{lis}</ul>')
    for ti, anchor in TABLE_PLACEMENT.items():
        if anchor == section_anchor:
            lines.append(render_table(tables_data[ti]))
    return '\n'.join(lines)

def render_section(sec, is_toplevel=True):
    anchor = sec['anchor']
    title = html_mod.escape(sec['title'])
    level = sec['level']
    content_html = render_content(sec.get('content_before_children', []), anchor)
    children_html = ''
    for child in sec.get('children', []):
        children_html += render_section(child, is_toplevel=False)
    if is_toplevel and level == 1:
        return f'<details class="reader__section" open id="{anchor}">\n<summary class="reader__section-title">{title}</summary>\n<div class="reader__section-body">\n{content_html}\n{children_html}\n</div>\n</details>'
    elif level == 2:
        return f'<h4 class="reader__subsection" id="{anchor}">{title}</h4>\n{content_html}\n{children_html}'
    elif level == 3:
        return f'<h5 class="reader__subsubsection" id="{anchor}">{title}</h5>\n{content_html}\n{children_html}'
    else:
        return f'{content_html}\n{children_html}'

# ── Header ──
header_parts = []
for item in root_content:
    text = item.get('text', '')
    if not text:
        continue
    if text == 'UNIR':
        header_parts.append(f'<p class="reader__org">{html_mod.escape(text)}</p>')
    elif 'Estratégia Lusófona' in text:
        header_parts.append(f'<p class="reader__subtitle">{html_mod.escape(text)}</p>')
    elif text.startswith('Documento Estratégico'):
        header_parts.append(f'<p class="reader__meta">{html_mod.escape(text)}</p>')
    elif text.startswith('Autor:'):
        header_parts.append(f'<p class="reader__meta">{html_mod.escape(text)}</p>')
    elif text.startswith('Classificação:'):
        header_parts.append(f'<p class="reader__meta">{html_mod.escape(text)}</p>')
header_html = '\n'.join(header_parts)

# ── TOC sidebar ──
toc_entries = []
for sec in body_sections:
    if sec['level'] == 1:
        toc_entries.append({'title': sec['title'], 'anchor': sec['anchor'], 'level': 1})
        for child in sec.get('children', []):
            if child['level'] == 2:
                toc_entries.append({'title': child['title'], 'anchor': child['anchor'], 'level': 2})

sidebar_toc = ''
for item in toc_entries:
    cls = 'reader__toc-link--sub' if item['level'] == 2 else ''
    sidebar_toc += f'<li class="{cls}"><a href="#{item["anchor"]}" class="reader__toc-link">{html_mod.escape(item["title"])}</a></li>\n'

# ── Body ──
body_parts = []
for sec in body_sections:
    body_parts.append(render_section(sec, is_toplevel=True))
body_html = '\n'.join(body_parts)

# ── Article HTML ──
article_html = f'''<div class="reader__progress" id="progressBar"><div class="reader__progress-fill" id="progressFill"></div></div>

<article class="reader">

<aside class="reader__sidebar">
  <nav class="reader__toc">
    <h4 class="reader__toc-title">Indice</h4>
    <ol>
{sidebar_toc}
    </ol>
  </nav>
</aside>

<div class="reader__body">

<header class="reader__header">
{header_html}
<h1 class="reader__title">PORTUGAL NO MUNDO MULTIPOLAR</h1>
</header>

<div class="reader__content">
{body_html}
</div>

<footer class="reader__footer">
  <p>Documento Estrategico &middot; UNIR &mdash; Unidos pela Nacao, Inovacao e Responsabilidade</p>
  <p>Maio 2026 &middot; Classificacao: Publico</p>
</footer>

</div>
</article>

<script>
(function(){{
  var tocLinks = document.querySelectorAll('.reader__toc-link');
  var headings = document.querySelectorAll('.reader__section[id], .reader__subsection[id]');
  if (!headings.length) return;
  var observer = new IntersectionObserver(function(entries){{
    entries.forEach(function(e){{
      if (e.isIntersecting) {{
        tocLinks.forEach(function(l){{ l.classList.remove('reader__toc-link--active'); }});
        var link = document.querySelector('.reader__toc-link[href="#' + e.target.id + '"]');
        if (link) link.classList.add('reader__toc-link--active');
      }}
    }});
  }}, {{root: document.getElementById('readerModal'), rootMargin: '-10% 0px -75% 0px'}});
  headings.forEach(function(h){{ observer.observe(h); }});
}})();
</script>'''

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(article_html)

# Stats
pc = article_html.count('<p class="reader__topic">')
pl = article_html.count('<ul class="reader__pillar-list">')
print(f"OK: {OUT_HTML} ({len(article_html)} bytes)")
print(f"   Sections: {len(body_sections)}, Tables: {article_html.count('<table class=')}")
print(f"   Topics: {pc}, Pillar lists: {pl}")
