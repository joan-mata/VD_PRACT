// ============================================================
// nav.js — Barra de progreso superior y puntos de navegación lateral
// ============================================================

const SECTIONS = [
  { id: "cover",      label: "Portada" },
  { id: "explore",    label: "Exploración" },
  { id: "act1",       label: "Acto 1 · Entorno & Conflictividad" },
  { id: "act2",       label: "Acto 2 · Gestión de Riesgo" },
  { id: "act3",       label: "Acto 3 · Factor Humano" },
  { id: "conclusion", label: "Conclusión & Ética" },
];

// ─── Progress bar ────────────────────────────────────────────
// Calculates page scroll progress percentage and updates top progress bar width
function updateProgressBar() {
  const bar = document.getElementById("progress-bar");
  if (!bar) return;
  const scrollTop    = window.scrollY;
  const docHeight    = document.documentElement.scrollHeight - window.innerHeight;
  const pct          = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  bar.style.width    = `${Math.min(pct, 100)}%`;
}

// ─── Side nav dots ───────────────────────────────────────────
// Builds the side dots indicator list based on SECTIONS configuration
function buildNavDots() {
  const nav = document.getElementById("side-nav");
  if (!nav) return;

  SECTIONS.forEach(({ id, label }) => {
    const dot = document.createElement("div");
    dot.className   = "nav-dot";
    dot.dataset.target = id;

    const lbl = document.createElement("span");
    lbl.className = "dot-label";
    lbl.textContent = label;
    dot.appendChild(lbl);

    dot.addEventListener("click", () => {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth" });
    });

    nav.appendChild(dot);
  });
}

// Highlights active side navigation dot based on current scroll position
function updateActiveDot() {
  const dots = document.querySelectorAll(".nav-dot");
  const midY = window.innerHeight * 0.45;

  let closest    = null;
  let closestDist = Infinity;

  SECTIONS.forEach(({ id }) => {
    const el = document.getElementById(id);
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const center = rect.top + rect.height / 2;
    const dist   = Math.abs(center - midY);
    if (dist < closestDist) {
      closestDist = dist;
      closest     = id;
    }
  });

  dots.forEach(dot => {
    dot.classList.toggle("active", dot.dataset.target === closest);
  });
}

// ─── Scroll-reveal via IntersectionObserver ──────────────────
// Initializes scroll reveal triggers to add the 'visible' class when elements enter the screen
function initReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        }
      });
    },
    { threshold: 0.12 }
  );

  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
}

// ─── Init ─────────────────────────────────────────────────────
function initNav() {
  buildNavDots();

  window.addEventListener("scroll", () => {
    updateProgressBar();
    updateActiveDot();
  }, { passive: true });

  // Initial state
  updateProgressBar();
  updateActiveDot();
  initReveal();
}

document.addEventListener("DOMContentLoaded", initNav);
