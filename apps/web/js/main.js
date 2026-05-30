// === CONFIGURAÇÃO ===
const ASSINATURAS_NECESSARIAS = 7500;
let currentCount = 0;

// Sheet API endpoint
// Servidor Python local: corre com `python3 signature_server.py`
// Se não estiver a correr, os dados ficam guardados no browser (localStorage)
const SHEET_API_URL = 'http://localhost:8080';

// === ELEMENTOS DOM ===
const counterEl = document.getElementById('counterNumber');
const remainingEl = document.getElementById('remainingCount');
const signatureCountEl = document.getElementById('signatureCount');
const progressFill = document.getElementById('progressFill');
const remainingNumber = document.getElementById('remainingNumber');

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

updateAllCounters(currentCount);

// === NAVEGAÇÃO ENTRE PASSOS ===
let currentStep = 1;

function showStep(step) {
  document.querySelectorAll('.form__step').forEach(el => el.classList.remove('form__step--active'));
  const el = document.getElementById('step' + step);
  if (el) el.classList.add('form__step--active');
}

function nextStep() {
  if (currentStep < 3) {
    if (currentStep === 1) {
      const email = document.getElementById('email').value.trim();
      const name = document.getElementById('name').value.trim();
      const postal = document.getElementById('postal').value.trim();
      const morada = document.getElementById('morada').value.trim();
      const cc = document.getElementById('cc').value.trim();
      const nascimento = document.getElementById('nascimento').value;

      if (!email || !name || !postal || !morada || !cc || !nascimento) {
        alert('Preenche todos os campos. É obrigatório por lei para formalizar a assinatura.');
        return;
      }
      if (cc.length < 6) {
        alert('Número de Cartão de Cidadão inválido.');
        return;
      }
    }
    if (currentStep === 2) {
      const checked = document.querySelectorAll('#step2 input[type="checkbox"]:checked');
      if (checked.length === 0) {
        alert('Escolhe pelo menos uma área. Ajuda-nos a saber o que é prioritário para ti.');
        return;
      }
    }
    currentStep++;
    showStep(currentStep);
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    showStep(currentStep);
  }
}

// === SUBMISSÃO ===
document.getElementById('signupForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const data = {
    nome: document.getElementById('name').value.trim(),
    email: document.getElementById('email').value.trim(),
    postal: document.getElementById('postal').value.trim(),
    morada: document.getElementById('morada').value.trim(),
    cc: document.getElementById('cc').value.trim(),
    nascimento: document.getElementById('nascimento').value,
    interesses: Array.from(document.querySelectorAll('#step2 input[type="checkbox"]:checked')).map(cb => cb.value).join(','),
    quota: document.querySelector('input[name="quota"]:checked')?.value || '0',
    consentimento: 'Sim'
  };

  // 1. Guardar localmente (backup)
  const submissions = JSON.parse(localStorage.getItem('unir_signups') || '[]');
  submissions.push({...data, timestamp: new Date().toISOString()});
  localStorage.setItem('unir_signups', JSON.stringify(submissions));

  // 2. Escrever na Sheet via servidor local
  fetch(SHEET_API_URL, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(r => r.json()).then(res => {
    console.log('Sheet response:', res);
  }).catch(err => {
    console.log('Servidor local nao disponivel, dados guardados localmente');
  });

  // 3. Incrementar contador
  currentCount++;
  updateAllCounters(currentCount);

  // 4. Mostrar sucesso
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
