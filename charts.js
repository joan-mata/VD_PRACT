// ============================================================
// charts.js — Lógica de gráficos y mapa interactivo
// ============================================================

import {
  SUMMARY_STATS,
  CATEGORIES,
  RANGOS,
  COMITES,
  TERRITORIES,
  REFEREES,
  PARTIDOS
} from "./data.js";

// ─── Variables de Estado Global ──────────────────────────────
let activeCategoryIdx = -1; // -1 significa "Todos"
let activeComiteIdx = -1;   // -1 significa "Todos"
let map = null;
let markersLayerGroup = null;
let chartIstCards = null;
let chartIdpExp = null;

// ─── Formato numérico local (coma decimal) ──────────────────
function fmt(val, decimals = 2) {
  return val.toFixed(decimals).replace(".", ",");
}

// ─── Animación de Contadores ────────────────────────────────
function animateCounter(el, target, duration = 1000, decimals = 0, suffix = "") {
  if (!el) return;
  const start = performance.now();
  const startVal = 0;

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = startVal + (target - startVal) * eased;

    el.textContent = current.toFixed(decimals).replace(".", ",") + suffix;

    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ─── Inicialización de Filtros ──────────────────────────────
function initFilters() {
  const catSelect = document.getElementById("filter-category");
  const comSelect = document.getElementById("filter-comite");

  // Rellenar categorías
  CATEGORIES.forEach((cat, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.textContent = cat;
    catSelect.appendChild(opt);
  });

  // Rellenar comités
  COMITES.forEach((com, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.textContent = com;
    comSelect.appendChild(opt);
  });

  // Event Listeners
  catSelect.addEventListener("change", (e) => {
    activeCategoryIdx = e.target.value === "Todos" ? -1 : parseInt(e.target.value);
    updateDashboard();
  });

  comSelect.addEventListener("change", (e) => {
    activeComiteIdx = e.target.value === "Todos" ? -1 : parseInt(e.target.value);
    updateDashboard();
  });
}

// ─── Inicialización de Contadores de Portada ─────────────────
function initStatsCounters() {
  animateCounter(document.getElementById("stat-partidos"), SUMMARY_STATS.total_partidos_mapeados, 1200, 0, "");
  animateCounter(document.getElementById("stat-arbitros"), SUMMARY_STATS.total_arbitros, 1200, 0, "");
  animateCounter(document.getElementById("stat-mapeo"), SUMMARY_STATS.mapeo_pct, 1200, 1, "%");
  animateCounter(document.getElementById("stat-tarjetas"), SUMMARY_STATS.avg_tarjetas_global, 1200, 2, "");
}

// ─── Inicialización del Mapa Leaflet ─────────────────────────
function initMap() {
  // Centro aproximado de Cataluña
  map = L.map("map", {
    center: [41.65, 1.7],
    zoom: 8,
    minZoom: 7,
    maxZoom: 12,
    zoomControl: true
  });

  // Capa base en modo oscuro (CartoDB Dark Matter)
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(map);

  markersLayerGroup = L.layerGroup().addTo(map);
}

// ─── Escala de Colores para el IST ───────────────────────────
function getIstColor(ist) {
  if (ist < 85) return "#ef4444"; // Rojo: Bajo IST
  if (ist < 100) return "#f59e0b"; // Naranja/Amarillo: Medio-Bajo
  if (ist < 115) return "#60a5fa"; // Azul claro: Medio-Alto
  return "#1d4ed8"; // Azul oscuro: Alto IST
}

// ─── Calcular Estadísticas de Boxplot ────────────────────────
function getPercentile(sorted, percentile) {
  if (sorted.length === 0) return 0;
  const index = (percentile / 100) * (sorted.length - 1);
  if (Math.floor(index) === index) {
    return sorted[index];
  } else {
    const idx = Math.floor(index);
    const fraction = index - idx;
    return sorted[idx] + fraction * (sorted[idx + 1] - sorted[idx]);
  }
}

function calculateBoxplotStats(values) {
  if (values.length === 0) {
    return { min: 0, q1: 0, median: 0, q3: 0, max: 0, mean: 0 };
  }
  const sorted = [...values].sort((a, b) => a - b);
  const min = sorted[0];
  const max = sorted[sorted.length - 1];
  const median = getPercentile(sorted, 50);
  const q1 = getPercentile(sorted, 25);
  const q3 = getPercentile(sorted, 75);
  const sum = sorted.reduce((a, b) => a + b, 0);
  const mean = sum / sorted.length;
  
  return { min, q1, median, q3, max, mean };
}

// ─── Calcular Regresión Lineal ──────────────────────────────
function calculateRegression(points) {
  const n = points.length;
  if (n === 0) return [];
  let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
  for (let p of points) {
    sumX += p.x;
    sumY += p.y;
    sumXY += p.x * p.y;
    sumXX += p.x * p.x;
  }
  const denom = n * sumXX - sumX * sumX;
  if (denom === 0) return []; // Evitar división por cero
  
  const slope = (n * sumXY - sumX * sumY) / denom;
  const intercept = (sumY - slope * sumX) / n;
  
  const minX = Math.min(...points.map(p => p.x));
  const maxX = Math.max(...points.map(p => p.x));
  
  return [
    { x: minX, y: slope * minX + intercept },
    { x: maxX, y: slope * maxX + intercept }
  ];
}

// ─── Actualización del Panel de Detalles ──────────────────────
function updateDetailPanel(muniData, matchesCount, avgCards) {
  const panel = document.getElementById("detail-panel");
  if (!panel) return;

  const istClass = muniData.ist < 85 ? "low-ist" : (muniData.ist > 115 ? "high-ist" : "");
  
  // Renderizar estadios
  let stadiumItemsHTML = "";
  if (muniData.stadiums && muniData.stadiums.length > 0) {
    muniData.stadiums.forEach(stad => {
      stadiumItemsHTML += `
        <div class="stadium-item">
          <span class="stadium-name" title="${stad.name}">${stad.name}</span>
          <span class="stadium-meta">
            ${stad.partidos} part. · <span class="stadium-cards">${fmt(stad.avg_tarjetas, 2)} 🟨🟥</span>
          </span>
        </div>
      `;
    });
  } else {
    stadiumItemsHTML = "<p style='font-size:0.8rem;color:var(--text-secondary);'>No hay estadios registrados.</p>";
  }

  const subtitle = muniData.ciudad === muniData.barrio 
    ? `Municipio: ${muniData.ciudad}` 
    : `Ciudad: ${muniData.ciudad} | Barrio: ${muniData.barrio}`;

  panel.innerHTML = `
    <div class="panel-header">
      <h3 class="panel-title">${muniData.name}</h3>
      <p class="panel-subtitle">${subtitle}</p>
    </div>
    
    <div class="panel-stats-row">
      <div class="panel-stat-card">
        <span class="panel-stat-val ${istClass}">${fmt(muniData.ist, 1)}</span>
        <span class="panel-stat-lbl">Índice IST (Idescat)</span>
      </div>
      <div class="panel-stat-card">
        <span class="panel-stat-val">${fmt(avgCards, 2)}</span>
        <span class="panel-stat-lbl">Tarjetas / Partido</span>
      </div>
      <div class="panel-stat-card" style="grid-column: 1 / -1;">
        <span class="panel-stat-val">${matchesCount}</span>
        <span class="panel-stat-lbl">Partidos Registrados</span>
      </div>
    </div>
    
    <div class="stadium-list-wrap">
      <h4 class="stadium-list-title">Estadios / Campos locales</h4>
      <div class="stadium-list">
        ${stadiumItemsHTML}
      </div>
    </div>
  `;
}

// ─── ACTUALIZACIÓN COMPLETA DEL DASHBOARD ────────────────────
function updateDashboard() {
  console.log(`Filtros Aplicados - Categoria ID: ${activeCategoryIdx}, Comite ID: ${activeComiteIdx}`);

  // 1. Filtrar partidos y agrupar por municipio
  const muniAgg = {};
  const boxplotVets = { Bajo: [], Medio: [], Alto: [] };
  
  PARTIDOS.forEach(part => {
    const [muniIdx, tarjetas, catIdx, comiteIdx, refVet] = part;

    // Aplicar filtros
    if (activeCategoryIdx !== -1 && catIdx !== activeCategoryIdx) return;
    if (activeComiteIdx !== -1 && comiteIdx !== activeComiteIdx) return;

    // Agregación del municipio
    if (!muniAgg[muniIdx]) {
      muniAgg[muniIdx] = { partidos: 0, tarjetas: 0 };
    }
    muniAgg[muniIdx].partidos += 1;
    muniAgg[muniIdx].tarjetas += tarjetas;

    // Agregación para boxplot (veteranía vs IST del municipio)
    if (refVet !== null) {
      const ist = TERRITORIES[muniIdx].ist;
      if (ist < 85) {
        boxplotVets.Bajo.push(refVet);
      } else if (ist > 115) {
        boxplotVets.Alto.push(refVet);
      } else {
        boxplotVets.Medio.push(refVet);
      }
    }
  });

  // 2. Dibujar marcadores en el mapa Leaflet
  markersLayerGroup.clearLayers();
  
  const scatterPoints = [];

  Object.keys(muniAgg).forEach(muniIdxStr => {
    const muniIdx = parseInt(muniIdxStr);
    const data = TERRITORIES[muniIdx];
    const stats = muniAgg[muniIdx];
    const avgCards = stats.tarjetas / stats.partidos;

    // Añadir al scatter plot
    scatterPoints.push({
      x: data.ist,
      y: avgCards,
      name: data.name,
      partidos: stats.partidos
    });

    // Calcular radio proporcional a partidos (con límites para visibilidad)
    const radius = Math.max(5, Math.min(22, 4 + Math.sqrt(stats.partidos) * 0.45));
    const color = getIstColor(data.ist);

    const marker = L.circleMarker([data.lat, data.lng], {
      radius: radius,
      fillColor: color,
      color: "#080b11",
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.65
    });

    const subtitleTooltip = data.ciudad === data.barrio 
      ? `Municipio: ${data.ciudad}` 
      : `Ciudad: ${data.ciudad}<br>Barrio: ${data.barrio}`;

    // Tooltip simple
    marker.bindTooltip(`<strong>${data.name}</strong><br>${subtitleTooltip}<br>Partidos: ${stats.partidos}<br>IST: ${fmt(data.ist, 1)}`, {
      direction: "top",
      sticky: true,
      className: "custom-leaflet-tooltip"
    });

    // Al hacer clic, actualizar panel de detalles
    marker.on("click", () => {
      updateDetailPanel(data, stats.partidos, avgCards);
    });

    // Al pasar por encima, también actualizar para fluidez
    marker.on("mouseover", () => {
      updateDetailPanel(data, stats.partidos, avgCards);
    });

    markersLayerGroup.addLayer(marker);
  });

  // 3. Actualizar Scatter Plot (IST vs Tarjetas)
  const regPoints = calculateRegression(scatterPoints);
  
  if (chartIstCards) {
    chartIstCards.data.datasets[0].data = scatterPoints;
    chartIstCards.data.datasets[1].data = regPoints;
    chartIstCards.update();
  } else {
    const ctx = document.getElementById("chart-ist-cards").getContext("2d");
    chartIstCards = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Territorios",
            data: scatterPoints,
            backgroundColor: "rgba(96, 165, 250, 0.5)",
            borderColor: "#3b82f6",
            borderWidth: 1,
            pointRadius: 5,
            pointHoverRadius: 8
          },
          {
            label: "Recta de Tendencia",
            data: regPoints,
            type: "line",
            borderColor: "#ef4444",
            borderWidth: 2.5,
            fill: false,
            pointRadius: 0,
            showLine: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#f8fafc" }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                if (context.datasetIndex === 0) {
                  const pt = context.raw;
                  return `${pt.name} (IST: ${fmt(pt.x, 1)}, Tarjetas/Partido: ${fmt(pt.y, 2)}, Partidos: ${pt.partidos})`;
                }
                return "Línea de tendencia";
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Índice IST (Menor = Más vulnerable)", color: "#94a3b8" },
            ticks: { color: "#94a3b8" },
            grid: { color: "rgba(255,255,255,0.05)" }
          },
          y: {
            title: { display: true, text: "Media de Tarjetas por Partido", color: "#94a3b8" },
            ticks: { color: "#94a3b8" },
            grid: { color: "rgba(255,255,255,0.05)" }
          }
        }
      }
    });
  }

  // 4. Actualizar Boxplots
  const ranges = ["Bajo", "Medio", "Alto"];
  ranges.forEach(rango => {
    const stats = calculateBoxplotStats(boxplotVets[rango]);
    const cleanId = rango.toLowerCase();
    
    // Animar la mediana y la media
    animateCounter(document.getElementById(`box-${cleanId}-median`), stats.median, 600, 1, " a.");
    animateCounter(document.getElementById(`box-${cleanId}-mean`), stats.mean, 600, 1, " a.");
    
    // Asignar los demás percentiles
    document.getElementById(`box-${cleanId}-max`).textContent = `${stats.max.toFixed(0)} años`;
    document.getElementById(`box-${cleanId}-q3`).textContent = `${stats.q3.toFixed(0)} años`;
    document.getElementById(`box-${cleanId}-q1`).textContent = `${stats.q1.toFixed(0)} años`;
    document.getElementById(`box-${cleanId}-min`).textContent = `${stats.min.toFixed(0)} años`;
  });

  // 5. Filtrar Árbitros y Actualizar Scatter Plot IDP vs Experiencia (coloreado por rango FCA)
  // Paleta: gris → índigo → verde → ámbar → rojo (de menor a mayor rango)
  const rangoColors = [
    { bg: "rgba(148,163,184,0.6)", border: "#94a3b8" }, // 0 Cursetista
    { bg: "rgba(99,102,241,0.6)",  border: "#6366f1" }, // 1 3a Cat / Sit.Especial
    { bg: "rgba(52,211,153,0.6)",  border: "#34d399" }, // 2 2a Catalana
    { bg: "rgba(245,158,11,0.6)",  border: "#f59e0b" }, // 3 1a Cat / Élite
    { bg: "rgba(239,68,68,0.6)",   border: "#ef4444" }, // 4 3a Fed · Nacional
  ];

  const refScatterData = RANGOS.map(() => []);

  REFEREES.forEach(ref => {
    if (activeCategoryIdx !== -1 && ref.cat_idx !== activeCategoryIdx) return;
    if (activeComiteIdx !== -1 && ref.comite_idx !== activeComiteIdx) return;
    if (ref.vet === null) return;

    const ri = ref.rango_idx ?? 0;
    refScatterData[ri].push({
      x: ref.vet,
      y: ref.idp,
      partidos: ref.partidos,
      label: ref.id
    });
  });

  const pointRadiusFn = (context) => {
    const pt = context.raw;
    return pt ? Math.max(3, Math.min(15, 3 + Math.sqrt(pt.partidos) * 0.5)) : 5;
  };

  if (chartIdpExp) {
    RANGOS.forEach((_, i) => {
      chartIdpExp.data.datasets[i].data = refScatterData[i];
    });
    chartIdpExp.update();
  } else {
    const ctx = document.getElementById("chart-idp-exp").getContext("2d");
    chartIdpExp = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: RANGOS.map((label, i) => ({
          label,
          data: refScatterData[i],
          backgroundColor: rangoColors[i].bg,
          borderColor: rangoColors[i].border,
          borderWidth: 1,
          pointRadius: pointRadiusFn
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#f8fafc" } },
          tooltip: {
            callbacks: {
              label: (context) => {
                const pt = context.raw;
                return `${pt.label} (${context.dataset.label}) · ${pt.x} anys · IDP: ${fmt(pt.y, 3)} · ${pt.partidos} partits`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Anys de Veterania (Experiència)", color: "#94a3b8" },
            ticks: { color: "#94a3b8" },
            grid: { color: "rgba(255,255,255,0.05)" }
          },
          y: {
            title: { display: true, text: "IDP (Desviació de Targetes vs Categoria)", color: "#94a3b8" },
            ticks: { color: "#94a3b8" },
            grid: { color: "rgba(255,255,255,0.05)" }
          }
        }
      }
    });
  }
}

// ─── Inicialización de los Tooltips del Footer ────────────────
function initTooltips() {
  document.querySelectorAll(".tooltip-btn-wrap").forEach(wrap => {
    const btn = wrap.querySelector(".tooltip-btn");
    const tip = wrap.querySelector(".tooltip-content");
    if (!btn || !tip) return;

    btn.addEventListener("mouseenter", () => {
      const rect = wrap.getBoundingClientRect();
      if (rect.top < 260) {
        tip.classList.add("tooltip--below");
      } else {
        tip.classList.remove("tooltip--below");
      }
    });

    btn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        wrap.classList.toggle("tooltip--open");
      }
      if (e.key === "Escape") {
        wrap.classList.remove("tooltip--open");
        btn.blur();
      }
    });
  });
}

// ─── Ejecución al Cargar el DOM ──────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initFilters();
  initStatsCounters();
  initMap();
  updateDashboard();
  initTooltips();
});
