# Guion del Vídeo Explicativo: PRACT2 - Proyecto de Visualización de Datos (UOC)

Este guion está diseñado para un vídeo de **5 minutos** (dentro del límite estricto de **4 a 6 minutos** del enunciado). Sigue fielmente la estructura de evaluación indicada por la UOC y está adaptado al **dashboard web interactivo**.

---

## Estructura del Vídeo y Distribución de Tiempos

```mermaid
gantt
    title Distribución del Tiempo del Vídeo (5 minutos totales)
    dateFormat  s
    axisFormat %S
    section Secciones
    1. Introducción y Proceso (20%)   :active, 0, 60s
    2. Datos y Preparación (15%)     : 60s, 105s
    3. Demo del Dashboard (20%)       : 105s, 165s
    4. Preguntas de Recerca (20%)     : 165s, 225s
    5. Interactividad y Accesibilidad (15%) : 225s, 270s
    6. Conclusiones y Reflexión (10%) : 270s, 300s
```

---

## Guion Segundo a Segundo

### 1. Proceso de Creación e Introducción [0:00 - 1:00] (20% de la nota)
* **Visual en pantalla**: Tu dashboard principal cargado en el navegador (`https://joanmata.com/VD/PRACT/index.html`). Transición por la portada con el título: *"Árbitros y Desigualdad: ¿Influye el entorno en el juego?"*.
* **Voz en off / Cámara**:
  > *"Hola, mi nombre es Joan Mata. Como árbitro en activo y estudiante de la UOC, he desarrollado este proyecto para analizar si las designaciones arbitrales en el fútbol base catalán responden adecuadamente a la conflictividad y al contexto socioeconómico del territorio, o si existen sesgos en la asignación de colegiados.*
  >
  > *El proceso de creación comenzó definiendo las 8 preguntas de investigación en la PRACT1. Para la visualización, he optado por un desarrollo web interactivo a medida utilizando HTML5, CSS y Javascript. He diseñado una interfaz en modo oscuro con una estética limpia, inspirada en la PAC3, que guía al usuario desde los indicadores globales hasta el comportamiento individual del árbitro."*

### 2. Conjunto de Datos y Preparación [1:00 - 1:45] (15% de la nota)
* **Visual en pantalla**: Código en VS Code de `aggregate_data.py` o el archivo de datos agregados `data.js`.
* **Voz en off**:
  > *"Para este estudio, hemos cruzado tres fuentes de datos:*
  > *1. Las actas oficiales de más de 46.000 partidos de la FCF, extraídas mediante scraping.*
  > *2. El censo del Comité de Árbitros con veteranía y edad.*
  > *3. El Índice Socioeconómico Territorial (IST) del Idescat de 2023.*
  >
  > *El principal reto técnico fue el cruce geográfico. Mediante un script de Python, mapeamos los campos a nivel de Agrupación Censal o municipio, logrando geolocalizar el 83,8% de los partidos. Además, mediante la API de datos abiertos de la Generalitat de Catalunya, descargamos las coordenadas UTM de cada municipio para pintar los puntos en el mapa. Para asegurar el rendimiento web, precomputamos los datos y métricas en local y los exportamos a un JSON optimizado, evitando cargar archivos pesados en el navegador. Por supuesto, anonimizamos las actas de los colegiados para proteger su privacidad."*

### 3. Presentación en Vivo (Demo) [1:45 - 2:45] (20% de la nota)
* **Visual en pantalla**: Grabación en vivo interactuando con la web. Pasa el cursor por el mapa de Cataluña en Leaflet, haz clic en un par de municipios y muestra cómo se actualiza instantáneamente el panel de detalles de la derecha (con sus estadios y tarjetas).
* **Voz en off**:
  > *"Naveguemos por la aplicación web. El dashboard está estructurado en tres áreas visuales:*
  > *En el Acto 1, disponemos de un mapa interactivo construido con Leaflet.js sobre una capa oscura. El tamaño de cada marcador indica el volumen de partidos jugados y el color codifica el IST, yendo del rojo para zonas vulnerables al azul para zonas estables.*
  >
  > *Al pasar el cursor sobre cualquier municipio, el panel lateral derecho se actualiza en tiempo real mostrando las tarjetas medias, partidos y el listado detallado de estadios locales con su conflictividad específica. En la parte superior, los filtros de Categoría y Comité Territorial recalculan dinámicamente todo el modelo en menos de 2 milisegundos."*

### 4. Preguntas Clave y Hallazgos [2:45 - 3:45] (20% de la nota)
* **Visual en pantalla**: Haz scroll hacia abajo y haz zoom en el gráfico de correlación (Scatter Plot IST vs Tarjetas) y en las tarjetas estadísticas de Boxplot.
* **Voz en off**:
  > *"El diseño analítico responde directamente a nuestras hipótesis:*
  > *Primero, ¿existe correlación entre nivel socioeconómico y tarjetas? El gráfico de dispersión con regresión lineal interactiva demuestra que a menor IST (hacia la izquierda del gráfico), la media de tarjetas por partido sube de forma constante, confirmando una mayor conflictividad ambiental.*
  >
  > *Segundo, la gestión del riesgo: ¿se asignan árbitros experimentados a zonas complejas? Los Boxplots de veteranía revelan que la mediana de experiencia en partidos en zonas de bajo IST es de 6 años, mientras que en zonas de alto IST desciende a 3 años. El factor organizativo humano actúa como mitigador, destinando a árbitros con mayor control de juego a los campos de mayor tensión."*

### 5. Interactividad y Accesibilidad [3:45 - 4:30] (15% de la nota)
* **Visual en pantalla**: Haz scroll hasta el gráfico del Acto 3 (IDP vs Experiencia). Pasa el ratón sobre los puntos (árbitros) para ver sus tooltips. Muestra los botones flotantes del footer.
* **Voz en off**:
  > *"La interactividad se extiende al comportamiento humano. En el tercer gráfico, representamos la punitividad del árbitro medida por su Índice de Desviación de Punitividad en relación con su veteranía. Vemos una distribución en embudo: los árbitros noveles muestran IDPs muy dispersos (sobre-reacción disciplinaria), mientras que la veteranía converge firmemente hacia el cero.*
  >
  > *En cuanto a la accesibilidad y el diseño inclusivo, se ha seguido la pauta WCAG de contraste y tipografía, y se ha evitado la escala semáforo rojo-verde, optando por una paleta rojo-azul apta para usuarios con daltonismo. Además, en el pie de página incluimos botones interactivos que detallan los aspectos éticos y técnicos del proyecto."*

### 6. Reflexión Final y Cierre [4:30 - 5:00] (10% de la nota)
* **Visual en pantalla**: Scroll final al pie de página mostrando el enlace a GitHub y los créditos.
* **Voz en off**:
  > *"Como conclusión, esta práctica me ha permitido contrastar datos científicos con mi experiencia en el campo como colegiado, comprobando que las variables socioeconómicas tienen impacto en el comportamiento deportivo y que las designaciones actúan de manera adaptativa.*
  >
  > *La principal limitación es el 16% de partidos no mapeados por falta de datos en el acta de origen, un aspecto a mejorar integrando geolocalizaciones automatizadas por geocoding.*
  >
  > *El código de la aplicación y la preparación está subido en mi GitHub, y la web está publicada en mi dominio joanmata.com. Muchas gracias por su atención."*
