// === CONTADOR ANIMADO ===
const counterEl = document.getElementById('counterNumber');
const finalCountEl = document.getElementById('finalCount');
let currentCount = 10432;

function animateCounter(element, target) {
  if (!element) return;
  const duration = 1500;
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

// Atualiza contador a cada 30s (simula tempo real)
function updateCounter() {
  const increment = Math.floor(Math.random() * 3) + 1;
  currentCount += increment;
  if (counterEl) animateCounter(counterEl, currentCount);
  if (finalCountEl) animateCounter(finalCountEl, currentCount);
}

if (counterEl) animateCounter(counterEl, currentCount);
if (finalCountEl) animateCounter(finalCountEl, currentCount);
setInterval(updateCounter, 30000);

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
        alert('Preenche o email e o nome para continuar.');
        return;
      }
    }
    if (currentStep === 2) {
      const checked = document.querySelectorAll('#step2 input[type="checkbox"]:checked');
      if (checked.length === 0) {
        alert('Escolhe pelo menos um tema de interesse.');
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

  console.log('📋 Dados submetidos:', data);

  // SIMULAÇÃO: guardar no localStorage
  const submissions = JSON.parse(localStorage.getItem('unir_signups') || '[]');
  submissions.push(data);
  localStorage.setItem('unir_signups', JSON.stringify(submissions));

  // Mostrar mensagem de sucesso
  document.getElementById('signupForm').style.display = 'none';
  const successMsg = document.getElementById('successMessage');
  successMsg.style.display = 'block';
  animateCounter(document.getElementById('finalCount'), currentCount);
});

// === HAMBURGUER MENU ===
document.getElementById('navToggle')?.addEventListener('click', function() {
  const links = document.getElementById('navLinks');
  links.classList.toggle('nav__links--open');
});

// === INTERSEÇÃO PARA ANIMAÇÕES DE SCROLL ===
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .step, .team__member').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});
