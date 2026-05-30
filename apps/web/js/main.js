// === CONFIGURAÇÃO ===
const ASSINATURAS_NECESSARIAS = 7500;

// Detetar caminho base automaticamente (funciona em subpastas GitHub Pages)
const BASE_PATH = window.location.pathname.replace(/\/$/, '');

// Corrigir links absolutos no DOM para funcionarem com subpasta
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a[href^="/"]').forEach(function(link) {
    const href = link.getAttribute('href');
    // Não modificar links externos ou âncoras
    if (href.startsWith('//') || href.startsWith('http')) return;
    // Se for uma âncora tipo /#assinar, manter
    if (href.startsWith('/#')) return;
    // Se for /candidatar, prefixar com o caminho base
    if (href === '/candidatar' || href.startsWith('/candidatar')) {
      link.setAttribute('href', BASE_PATH + '/candidatar/');
    }
    // Se for /documentos
    if (href === '/documentos' || href.startsWith('/documentos')) {
      link.setAttribute('href', BASE_PATH + '/documentos/');
    }
    // Se for /, apontar para a raiz com /unir-platform/
    if (href === '/') {
      link.setAttribute('href', BASE_PATH + '/');
    }
  });
});

// API endpoint
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8001'
  : 'https://api.unir.pt';

// Fallback para contagem local
let currentCount = 0;
const STORAGE_KEY = 'unir_signups';

// === ELEMENTOS DOM ===
const counterEl = document.getElementById('counterNumber');
const remainingEl = document.getElementById('remainingCount');
const signatureCountEl = document.getElementById('signatureCount');
const progressFill = document.getElementById('progressFill');
const remainingNumber = document.getElementById('remainingNumber');

function loadLocalCount() {
  try {
    const submissions = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    currentCount = submissions.length;
  } catch(e) {
    currentCount = 0;
  }
}

// === CONTADOR ANIMADO ===
function animateNumber(element, target, duration = 1500) {
  if (!element) return;
  const start = performance.now();
  const startVal = parseInt(element.textContent.replace(/,/g, '')) || 0;
  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.floor(startVal + (target - startVal) * eased);
    element.textContent = value.toLocaleString('pt-PT');
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

function updateAllCounters(value) {
  const remaining = Math.max(0, ASSINATURAS_NECESSARIAS - value);
  const progress = Math.min(100, (value / ASSINATURAS_NECESSARIAS) * 100);
  if (counterEl) animateNumber(counterEl, value);
  if (signatureCountEl) animateNumber(signatureCountEl, value);
  if (remainingEl) remainingEl.textContent = remaining.toLocaleString('pt-PT');
  if (remainingNumber) remainingNumber.textContent = remaining.toLocaleString('pt-PT');
  if (progressFill) progressFill.style.width = Math.min(100, progress) + '%';
}

loadLocalCount();
updateAllCounters(currentCount);

// === SUBMISSÃO ===
document.getElementById('signupForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'A registar...';

  const data = {
    email: document.getElementById('email').value.trim(),
    name: document.getElementById('name').value.trim(),
    postal: document.getElementById('postal').value.trim(),
    morada: document.getElementById('morada').value.trim(),
    cc: document.getElementById('cc').value.trim(),
    nascimento: document.getElementById('nascimento').value,
  };

  if (!data.email || !data.name || !data.postal || !data.morada || !data.cc || !data.nascimento) {
    alert('Preenche todos os campos. É obrigatório por lei para formalizar a assinatura.');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Assinar para Fundar';
    return;
  }
  if (data.cc.length < 6) {
    alert('Número de Cartão de Cidadão inválido.');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Assinar para Fundar';
    return;
  }

  const submissions = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  submissions.push({...data, timestamp: new Date().toISOString()});
  localStorage.setItem(STORAGE_KEY, JSON.stringify(submissions));

  try {
    const response = await fetch(API_URL + '/public/sign', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!result.success && result.message) {
      console.warn('API:', result.message);
    }
  } catch (err) {
    console.log('API indisponível, dados guardados localmente');
  }

  currentCount = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').length;
  updateAllCounters(currentCount);

  document.getElementById('signupForm').style.display = 'none';
  const successMsg = document.getElementById('successMessage');
  if (successMsg) successMsg.style.display = 'block';
});

// === HAMBURGUER ===
document.getElementById('navToggle')?.addEventListener('click', function() {
  document.getElementById('navLinks').classList.toggle('nav__links--open');
});

document.querySelectorAll('.nav__link').forEach(link => {
  link.addEventListener('click', function() {
    document.getElementById('navLinks').classList.remove('nav__links--open');
  });
});

// === COPIAR LINK ===
function copyLink() {
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    alert('Link copiado! Partilha com quem também quer um Portugal melhor.');
  }).catch(() => {
    const input = document.createElement('input');
    input.value = url;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    alert('Link copiado!');
  });
}

// === SCROLL ANIMATIONS ===
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .problem-card, .diff-item, .team__member, .signatures__step').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});
