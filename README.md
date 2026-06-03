# Árbitros y Desigualdad: ¿Influye el entorno en el juego? · PRACT2

Este repositorio contiene el dashboard interactivo y el análisis de la **PRACT2 de Visualización de Datos (UOC)**. El proyecto cruza las actas de partidos de la Federació Catalana de Futbol (temporada 25/26) con los índices socioeconómicos territoriales (IST) del Idescat para analizar si el entorno influye en la conflictividad deportiva y en la gestión táctica de las designaciones arbitrales.

## 🌐 Visualización en vivo
Puedes ver el dashboard funcionando en la siguiente dirección:
👉 **[joanmata.com/VD/PRACT/index.html](https://joanmata.com/VD/PRACT/index.html)**

> Para ejecutar localmente **sin servidor HTTP**, abre directamente `web/index_local.html` en el navegador. Solo requiere conexión a internet para Leaflet.js y Chart.js (CDN).

## 📂 Estructura de archivos del repositorio

- **`web/index.html`**: Dashboard principal (requiere servidor HTTP o live-server).
- **`web/index_local.html`**: Versión standalone con CSS, datos y JS inline — apto para entrega offline.
- **`web/styles.css`**: Diseño visual con tema oscuro (*dark mode*), tipografías Outfit/Inter y layouts responsivos.
- **`web/data.js`**: Datos precomputados como módulo ES. Generado automáticamente por `aggregate_data.py`.
- **`web/charts.js`**: Lógica de interacción: mapa Leaflet, scatter plots con Chart.js, boxplots y filtros cruzados.
- **`web/nav.js`**: Navegación lateral con puntos, barra de progreso superior y efectos de revelado por scroll.

- **`data/clean_partidos.csv`**: Partidos limpios con territorio y categoría asignados.
- **`data/clean_arbitros.csv`**: Árbitros anonimizados con veteranía e IDP calculado.
- **`data/dim_territorio.csv`**: Dimensión territorial (IST, coordenadas, agrupación censal).
- **`data/stadium_to_ist_mapping.csv`**: Mapeo de estadios a territorio e IST.

- **`prepare_data.py`**: Limpieza y preprocesamiento de los datos brutos de la FCF.
- **`aggregate_data.py`**: Agregación territorial y generación del módulo `web/data.js`.
- **`guion_video_pract2.md`**: Guion del vídeo de presentación de la práctica.
- **`acceso_pract2.txt`**: Ficha de entrega con URLs, fuentes y nota sobre ética.

## 🛠️ Tecnologías utilizadas

- **Vanilla JavaScript (ES6+):** Programación modular sin dependencias propias.
- **Leaflet.js:** Mapa interactivo con tiles CartoDB Dark Matter y marcadores parametrizados por IST.
- **Chart.js:** Scatter plots de correlación IST–tarjetas e IDP–experiencia con regresión lineal.
- **CSS Moderno:** Variables CSS, Grid, Flexbox y animaciones nativas.
- **Intersection Observer API:** Revelado de elementos al hacer scroll.
- **Python (pandas):** Limpieza, geolocalización territorial y generación del módulo de datos.

## 📊 Fuentes de datos

- **FCF (Federació Catalana de Futbol):** Actas de partidos temporada 25/26 — 44.193 partidos, 2.110 árbitros.
- **Idescat:** Índice Socioeconómico Territorial (IST) 2023, desagregado a nivel de agrupación censal y municipio.

## 🔒 Ética y Privacidad

El NIF de todos los colegiados fue eliminado en la fase de preprocesamiento. Los nombres reales han sido sustituidos por identificadores anónimos (`COL_XXXX`) en todos los ficheros y en la visualización. Los datos se usan exclusivamente con fines académicos en el marco del máster de Data Science de la UOC.

---
**Autor:** Joan Mata Parraga  
**Asignatura:** Visualització de les Dades  
**Grado:** Ciencia de Datos (UOC)
