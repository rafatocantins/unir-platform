// === CONFIGURAÇÃO ===
const ASSINATURAS_NECESSARIAS = 7500;
let currentCount = 0;  // valor real — começa a 0, sobe com cada submissão

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

// Inicializar contadores
updateAllCounters(currentCount);

// Simular atualização a cada 45s (para demonstração)
function simulateNewSignature() {
  // Só simula se tiver menos de 7500
  if (currentCount < ASSINATURAS_NECESSARIAS) {
    const increment = Math.floor(Math.random() * 2) + 1;
    currentCount += increment;
    updateAllCounters(currentCount);
  }
}
setInterval(simulateNewSignature, 45000);

// === NAVEGAÇÃO ENTRE PASSOS DO FORMULÁRIO ===
let currentStep = 1;

function showStep(step) {
  document.querySelectorAll('.form__step').forEach(el => el.classList.remove('form__step--active'));
  const el = document.getElementById(`step${step}`);
  if (el) el.classList.add('form__step--active');
}

function nextStep() {
  if (currentStep < 3) {
    if (currentStep === 1) {
      const email = document.getElementById('email').value.trim();
      const name = document.getElementById('name').value.trim();
      if (!email || !name) {
        alert('Preenche o email e o nome para continuares. É rápido.');
        return;
      }
    }
    if (currentStep === 2) {
      const checked = document.querySelectorAll('#step2 input[type="checkbox"]:checked');
      if (checked.length === 0) {
        alert('Escolhe pelo menos um tema. Saber o que te interessa ajuda-nos a priorizar.');
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

// === SUBMISSÃO DO FORMULÁRIO ===
document.getElementById('signupForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const data = {
    email: document.getElementById('email').value.trim(),
    name: document.getElementById('name').value.trim(),
    postal: document.getElementById('postal').value.trim(),
    interests: Array.from(document.querySelectorAll('#step2 input[type="checkbox"]:checked')).map(cb => cb.value),
    quota: document.querySelector('input[name="quota"]:checked')?.value || '0',
    customQuota: document.getElementById('customQuota').value || null,
    timestamp: new Date().toISOString()
  };

  // Guardar no localStorage
  const submissions = JSON.parse(localStorage.getItem('unir_signups') || '[]');
  submissions.push(data);
  localStorage.setItem('unir_signups', JSON.stringify(submissions));

  // Incrementar contador real
  currentCount++;
  updateAllCounters(currentCount);

  // Mostrar mensagem de sucesso
  document.getElementById('signupForm').style.display = 'none';
  const successMsg = document.getElementById('successMessage');
  successMsg.style.display = 'block';
});

// === HAMBURGUER MENU ===
document.getElementById('navToggle')?.addEventListener('click', function() {
  const links = document.getElementById('navLinks');
  links.classList.toggle('nav__links--open');
});

// === FECHAR MENU AO CLICAR NUM LINK ===
document.querySelectorAll('.nav__link').forEach(link => {
  link.addEventListener('click', function() {
    document.getElementById('navLinks').classList.remove('nav__links--open');
  });
});

// === ANIMAÇÕES DE SCROLL ===
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
