# Memoria del Proyecto de Visualización: PRACT2
**Asignatura:** Visualització de Dades (UOC)  
**Estudiante:** Joan Mata Parraga  
**Semestre:** Segundo Semestre  

---

## 1. Introducción y Objetivos
Este proyecto representa la consolidación práctica del diseño propuesto en la **PRACT1**. Como árbitro de fútbol en activo, la motivación principal de este estudio es explorar la relación empírica entre el **contexto socioeconómico** de las zonas donde se disputan partidos de fútbol base en Cataluña (medido por el **Índice Socioeconómico Territorial - IST** de Idescat) y la **conflictividad deportiva** (medida a través del volumen de tarjetas amarillas y rojas). 

Asimismo, se analiza la **toma de decisiones organizacionales**: cómo se designan los árbitros en función de su perfil (edad, veteranía y categoría oficial) en escenarios de potencial riesgo social (zonas con bajo IST) y el impacto del factor humano en la disciplina del juego (mediante el cálculo del **Índice de Desviación de Punitividad - IDP**).

El objetivo es construir un cuadro de mando interactivo a medida en formato de **aplicación web interactiva (HTML5, CSS3, JS Vanilla, Leaflet.js y Chart.js)** que permita responder de forma visual, fluida y científica a las 8 preguntas de investigación planteadas al inicio del curso, mejorando sustancialmente las limitaciones interactivas y estéticas de las plataformas de Business Intelligence cerradas.

---

## 2. Preparación y Calidad de los Datos (Data Prep)
La preparación de los datos constituyó el principal reto de ingeniería del proyecto. El procesamiento se divide en dos fases automatizadas: la limpieza y el mapeo espacial.

### 2.1. El Reto del Mapeo Geográfico
El dataset de partidos (`fcf_analytics_2526.csv`) contiene el nombre del estadio (ej: *CAMP DE FUTBOL MPAL. DE TÉRMENS*) y el de los equipos locales, pero carece de un identificador geográfico o de coordenadas que permitan cruzarlo directamente con el archivo del IST (`ist14034ac.csv`) a nivel de **Agrupación Censal** (barrio).

Para resolver esto, implementamos un algoritmo de emparejamiento de texto en Python (`prepare_data.py`) que opera de la siguiente manera:
1. **Normalización de Texto**: Se eliminaron acentos, mayúsculas y caracteres de puntuación, y se estandarizaron abreviaturas habituales del fútbol catalán (ej: *ST. -> SANT*, *STA. -> SANTA*, *MPAL. -> MUNICIPAL*).
2. **Patrones Específicos**: Se creó un diccionario de expresiones regulares para identificar barrios y estadios icónicos con características socioeconómicas muy definidas (ej: *La Mina, Sant Roc, Llefià, El Raval, Sant Gervasi, Can Dragó, Rocafonda*).
3. **Búsqueda por Municipio e IST Municipal**:
   - Si el estadio o equipo contenía el nombre de un municipio con múltiples agrupaciones censales (las 247 ciudades más pobladas de Cataluña), se le asignó la primera agrupación censal del municipio de forma predeterminada, a menos que un patrón de barrio específico indicara lo contrario.
   - Si el municipio era de menor población y no figuraba desglosado por barrios en el IST de agrupaciones censales, se realizó un **cruce de fallback** con la tabla de IST a nivel de municipio (`ist14034mun.csv`).

**Resultado del Mapeo**:
* Combinaciones únicas de estadio-equipo local: **2.699**.
* Estadios mapeados con éxito a una clave territorial: **2.216** (**82,10%**).
* Total de partidos enriquecidos con éxito: **39.137 de 46.715** (**83,78%**).

### 2.2. Geolocalización de Municipios (Leaflet)
Dado que Leaflet.js en el frontend requiere coordenadas geográficas de latitud y longitud para pintar los puntos de los estadios, se desarrolló un segundo script (`aggregate_data.py`). Este script descarga de forma automatizada el catálogo oficial de **Capitales de Municipios Georreferenciadas** de la Generalitat de Catalunya (`analisi.transparenciacatalunya.cat`) y cruza los municipios mapeados para asignarles sus coordenadas UTM/decimales correspondientes. Se geolocalizaron con éxito **384 de 386 municipios** únicos del dataset (una tasa de acierto del **99,48%**).

### 2.3. Construcción de Métricas Propias
* **Edad del Árbitro**: Calculada restando el año de nacimiento (`F. Naixem.`) al año actual (2026).
* **Veteranía en el CTA**: Años transcurridos desde la fecha de alta del colegiado en el Comité Técnico de Árbitros.
* **IDP (Índice de Desviación de Punitividad)**: Calcula qué tan estricto es un árbitro en comparación con sus compañeros de categoría. 
  $$\text{Desviación del Partido} = \text{Tarjetas Partido} - \text{Media Tarjetas de su Categoría}$$
  El IDP del árbitro es la media de estas desviaciones en todos los partidos que ha dirigido. Un IDP positivo (ej: +1.2) indica que el árbitro muestra en promedio 1.2 tarjetas más por partido que la media de la categoría (Amateur, Juvenil, Cadete) en la que pita.

### 2.4. Ética y Privacidad de los Datos (Competencia C1)
Para cumplir con las directrices éticas propuestas en la PRACT1:
- Se eliminaron por completo las columnas de identificación fiscal (**NIF**) del dataset de árbitros antes de realizar cualquier exportación.
- Aunque el dataset de partidos en bruto contiene el nombre del árbitro para realizar los joins, la visualización web únicamente expone un identificador anonimizado (`COL_XXXX`) en los detalles interactivos, garantizando que el análisis se centre en perfiles demográficos y no en señalamientos individuales.

---

## 3. Arquitectura del Modelo de Datos (Modelo de Agregación Web)
Para optimizar el rendimiento de la aplicación web y evitar cargar un archivo CSV de $40.000$ filas en el navegador (lo cual ralentizaría la carga y bloquearía el hilo de ejecución principal en dispositivos móviles), se estructuró un sistema de precomputación en Python (`aggregate_data.py`). El script procesa la base de datos relacional y exporta los datos compactados a un archivo modular `web/data.js` con las siguientes estructuras:

* **SUMMARY_STATS**: Métricas globales precargadas (partidos totales, media de tarjetas, tasa de geolocalización, etc.).
* **MUNICIPALITIES**: Array de municipios con sus coordenadas (lat/lng), su IST y el top 6 de sus estadios locales con partidos y tarjetas medias.
* **REFEREES**: Array de árbitros activos con su veteranía, IDP, partidos dirigidos y la categoría y comité a los que pertenecen.
* **PARTIDOS**: Matriz compacta que representa los partidos a nivel de índices, permitiendo al motor de JS del frontend realizar agregaciones, filtrados de boxplot y cálculos de regresión lineal en menos de 2 milisegundos.

---

## 4. Diseño de las Visualizaciones e Interactividad

El cuadro de mando interactivo se ha estructurado siguiendo un diseño de scrollytelling dividido en secciones coherentes:

### 4.1. Mapa de Calor Territorial (Conflictividad vs IST)
* **Descripción**: Mapa interactivo de Cataluña (Leaflet.js) centrado sobre una capa base oscura (CartoDB DarkMatter) para resaltar los marcadores de datos.
* **Codificación Visual**:
  - **Tamaño del punto**: Volumen de partidos jugados en el municipio (mayor tamaño = más partidos).
  - **Color del punto**: Nivel de IST (escala divergente: Rojo para IST < 85 [Alerta/Vulnerabilidad], Naranja para IST 85–100, Azul claro para IST 100–115 y Azul oscuro para IST > 115).
* **Interacción**: Al pasar el cursor o hacer clic sobre cualquier municipio, el panel lateral de detalles se actualiza dinámicamente mostrando la ficha técnica del municipio: nombre, IST exacto, tarjetas promedio, partidos y el listado de estadios locales con su volumen y conflictividad individual.

### 4.2. Scatter Plot: Correlación IST vs Tarjetas
* **Descripción**: Gráfico de dispersión (Chart.js) con el valor IST en el eje X y la media de tarjetas por partido en el eje Y. Cada punto es un municipio.
* **Codificación Visual**: Se calcula y dibuja en tiempo real la recta de regresión lineal (mínimos cuadrados) sobre los puntos filtrados.
* **Propósito**: Responder a la *Pregunta 1 (Correlación Socioeconómica)*. Permite validar visualmente si la pendiente de la recta es negativa (a menor IST, más tarjetas).

### 4.3. Boxplot: Asignación de Árbitros (Gestión del Riesgo)
* **Descripción**: Tres tarjetas de visualización que exponen la distribución (mínimo, percentil 25, mediana/media, percentil 75 y máximo) de la veteranía de los árbitros designados según el IST del partido.
* **Propósito**: Responder a la *Pregunta 2 (Gestión del Riesgo)*. Evidencia que la mediana de experiencia de los colegiados es significativamente mayor en partidos en zonas de vulnerabilidad (6,0 años de veteranía media en bajo IST frente a 3,0 años en alto IST), demostrando la gestión activa de designaciones.

### 4.4. Scatter Plot: Estilo de Gestión (Punitividad vs Experiencia)
* **Descripción**: Gráfico de dispersión (Chart.js) con los años de veteranía en el eje X y el IDP (Desviación de Punitividad) en el eje Y.
* **Codificación Visual**: Puntos coloreados por la categoría oficial del árbitro (Cadete = Azul, Juvenil = Amarillo, Amateur = Rojo). El radio del punto indica el volumen de partidos pitados.
* **Propósito**: Responder a la *Pregunta 3 (Punitividad)* y *Pregunta 8 (Resiliencia)*. Permite verificar la convergencia en forma de embudo: los árbitros con menor veteranía cometen desviaciones disciplinarias extremas (IDPs alejados de 0), mientras que a mayor experiencia los puntos se concentran firmemente en torno a la media (IDP = 0).

---

## 5. Decisiones de Diseño y Accesibilidad
* **Storytelling**: Se utiliza una estructura narrativa de scrollytelling en modo oscuro. Guía al usuario desde el marco conceptual (portada y contadores rápidos) pasando por la visualización espacial macro (mapa de Cataluña), los contrastes institucionales (designaciones por riesgo) hasta llegar al comportamiento individual del árbitro (IDP).
* **Paleta de Colores**: Diseñada para garantizar la accesibilidad a usuarios con daltonismo (deuteranopía/protanopía). Se evitó la clásica combinación semafórica Rojo/Verde, seleccionando una escala divergente de **Rojo (Bajo IST / Alerta) a Azul (Alto IST / Estabilidad)**.
* **Filtros Cruzados Coordinados**: En la parte superior, los selectores de **Categoría** y **Comité Territorial** actualizan en cascada y de forma instantánea el mapa, los gráficos y el cálculo de la regresión lineal, permitiendo analizar de forma aislada la realidad de comités específicos (ej: Baix Llobregat o Girona).

---

## 6. Conclusiones y Limitaciones
* **Principales Hallazgos**: Las visualizaciones confirman la correlación negativa entre el IST y las tarjetas. La recta de regresión muestra una tendencia clara a un mayor número de tarjetas en entornos de bajo IST. El sistema de designación responde a este factor asignando colegiados con mayor promedio de veteranía a los partidos en zonas vulnerables.
* **Limitaciones**:
  - El 16,22% de partidos no mapeados puede generar un leve sesgo de representación, principalmente en campos de municipios muy pequeños cuyas actas oficiales no estaban estandarizadas en la web de la FCF.
  - El IST de Idescat corresponde a 2023, mientras que los partidos son de la temporada 2025/2026. Aunque el cambio estructural socioeconómico suele ser lento, puede existir alguna pequeña variación en el índice de determinados barrios.

---

## 7. Enlaces de Entrega

- **Dashboard Web Interactivo:** [[Enlace al Dashboard]](https://joanmata.com/VD/PRACT/index.html)
- **Repositorio de GitHub (Código, Datos y Frontend):** [[Enlace al Repositorio]](https://github.com/joan-mata/VD_PRACT.git)
- **Vídeo Explicativo del Proyecto:** [[Enlace al Vídeo]](https://youtu.be/refstats-demo-joanmata)
