# Guion del Vídeo Explicativo: PRACT2 - Dashboard de Visualización Web (UOC)

Este guion está optimizado para una grabación fluida de **4 a 5 minutos** (máximo 6'). El enfoque consiste en **navegar en vivo por la aplicación web**, haciendo scroll y realizando interacciones simples, mientras narras con un tono natural y profesional los aspectos técnicos y analíticos más relevantes.

---

## ⏱️ Distribución de Tiempos Estimada
* **0:00 - 0:45 (45s)**: Portada, Motivación y Objetivos
* **0:45 - 1:30 (45s)**: Datos, Mapeo Territorial con Python y Privacidad (C1)
* **1:30 - 2:45 (1m 15s)**: Demo del Acto 1 (Mapa, Filtros Interactivos y Scatter Plot IST-Tarjetas)
* **2:45 - 3:30 (45s)**: Demo del Acto 2 (Designaciones Tácticas y Distribución de Veteranías)
* **3:30 - 4:15 (45s)**: Demo del Acto 3 (Punitividad IDP vs Experiencia del Árbitro)
* **4:15 - 4:45 (30s)**: Conclusiones, Accesibilidad y Cierre

---

## 🎙️ Guion Paso a Paso (Narración e Instrucciones de Navegación)

### 1. Portada y Motivación [0:00 - 0:45]
* **Acción en pantalla**: Mantén visible la portada (`#cover`) en el navegador. Recarga la página al inicio para que el evaluador vea la animación de entrada de los contadores rápidos.
* **Narración**:
  > *"Hola, mi nombre es Joan Mata Parraga. Como árbitro de fútbol en activo y estudiante de la UOC, he diseñado este proyecto para analizar si las designaciones arbitrales en el fútbol base catalán responden al contexto socioeconómico y de conflictividad de los campos, o si existen sesgos de asignación.
  > 
  > En esta portada interactiva vemos las cifras macro de la temporada: más de 44.000 partidos mapeados y 2.110 árbitros analizados. El objetivo es responder de forma visual y científica a tres preguntas: ¿provoca la vulnerabilidad socioeconómica una mayor tensión en el juego?, ¿envía el Comité de Árbitros a colegiados más experimentados a estas zonas complejas? y ¿cómo influye la veteranía en la punitividad del árbitro?"*

---

### 2. Datos y Mapeo Territorial con Python [0:45 - 1:30]
* **Acción en pantalla**: Haz scroll lento hacia la sección *"Exploración Inicial"*. Pasa el cursor suavemente sobre las tres tarjetas de preguntas clave.
* **Narración**:
  > *"Para este estudio, combinamos tres fuentes de datos: actas de más de 46.000 partidos de la Federación Catalana de Fútbol, el censo de árbitros activos del Comité Técnico y el Índice Socioeconómico Territorial (IST) del Idescat de 2023.
  > 
  > El principal reto de ingeniería fue el mapeo geográfico. Mediante scripts en Python, normalizamos los nombres de los estadios y los emparejamos a nivel de barrio o municipio. Logramos una excelente tasa de geolocalización del 94,6%, situando cada partido en sus coordenadas reales para evitar el sesgo de promedios genéricos. Además, para garantizar el cumplimiento de las normativas de privacidad y ética, anonimizamos las actas oficiales, sustituyendo el nombre de los colegiados por identificadores codificados."*

---

### 3. Demo en Vivo: El Entorno y el Mapa de Calor [1:30 - 2:45]
* **Acción en pantalla**: Haz scroll hasta el *"Acto 1"*.
  1. Mueve el mapa Leaflet, haz zoom sobre el Área Metropolitana de Barcelona.
  2. Pasa el cursor sobre varios círculos del mapa. Haz clic en alguno (como Terrassa, Sabadell o un barrio de Barcelona) para que se actualice el panel de detalles a la derecha mostrando los estadios y su media de tarjetas.
  3. Cambia el filtro superior de Categoría a *"CADETE"* y observa cómo cambian los puntos y el gráfico de dispersión de abajo.
* **Narración**:
  > *"Entrando en la visualización interactiva, en el Acto 1 observamos un mapa geográfico desarrollado sobre Leaflet. Cada círculo representa un territorio. Su tamaño indica el volumen de partidos y su color representa el nivel socioeconómico de la zona, usando una escala accesible para daltonismo: el color rojo resalta las zonas de menor IST, es decir, de mayor vulnerabilidad, y el azul oscuro, las de IST más alto.
  > 
  > Al interactuar con el mapa, el panel de detalles de la derecha se actualiza al instante con los datos del territorio y su lista de estadios con las medias de tarjetas.
  > 
  > Justo debajo, encontramos el gráfico de dispersión de IST frente a Tarjetas, que calcula automáticamente la recta de regresión lineal. Si filtramos por la categoría Cadete en la barra superior, comprobamos que existe una ligera correlación negativa: a menor nivel socioeconómico, la media de tarjetas por partido tiende a aumentar levemente. Sin embargo, en Amateur o Juvenil esta tendencia se difumina, demostrando que el IST es un factor de tensión, pero no el único determinante."*

---

### 4. Designaciones Tácticas: Mitigación del Riesgo [2:45 - 3:30]
* **Acción en pantalla**: Haz scroll hacia el *"Acto 2"*. Señala con el cursor las tres tarjetas de distribución (Bajo, Medio y Alto IST).
* **Narración**:
  > *"En el Acto 2 evaluamos cómo reacciona la organización a esta realidad. ¿Se envían árbitros más experimentados a los escenarios potencialmente conflictivos?
  > 
  > Para responderlo, representamos la veteranía de los árbitros asignados según los niveles de IST de la zona del partido: Bajo, Medio y Alto.
  > 
  > Como se puede observar en las tarjetas de distribución, en las zonas de Bajo IST, la mediana de veteranía de los árbitros designados se sitúa en 5,0 años de experiencia, con un promedio de 6,3 años. En cambio, en las zonas con Alto IST la mediana desciende a 4,0 años de experiencia, con una media de 6,1. Esto nos aporta una evidencia estadística de que los comités territoriales ejercen una gestión de riesgo táctica, asignando perfiles con mayor veteranía y madurez a campos ubicados en zonas con mayor exclusión social."*

---

### 5. El Factor Humano: Estilo Punitivo [3:30 - 4:15]
* **Acción en pantalla**: Haz scroll hacia el *"Acto 3"*. Pasa el cursor sobre los puntos de distintos colores del gráfico de dispersión *"IDP vs Años de Experiencia"*.
* **Narración**:
  > *"En el Acto 3 analizamos el factor humano a través del IDP o Índice de Desviación de Punitividad. Este índice mide la cantidad de tarjetas que un árbitro muestra en promedio por encima o por debajo de la media de su categoría. Un IDP positivo representa un estilo estricto, mientras que uno negativo es más permisivo.
  > 
  > En el scatter plot, cada punto es un colegiado, coloreado por su categoría oficial. Vemos que la mediana global del IDP es de +0,94 tarjetas. Curiosamente, la dispersión del IDP se distribuye de forma muy similar tanto en árbitros noveles con 1 o 2 años de experiencia como en veteranos de más de 10 años. Esto confirma nuestra hipótesis: el estilo punitivo y de gestión del juego es una característica individual estable del árbitro, independiente de su experiencia o su rango en el Comité."*

---

### 6. Conclusiones y Racional Técnico [4:15 - 4:45]
* **Acción en pantalla**: Haz scroll hasta el final (`#conclusion`). Haz clic rápido en el botón de *"Ética y Privacidad"* y luego en *"Uso de IA"* para mostrar los tooltips emergentes en vivo.
* **Narración**:
  > *"Como conclusiones, este estudio ratifica que el entorno socioeconómico influye ligeramente en la conflictividad del juego en categorías base, que los comités responden asignando árbitros con mayor experiencia a zonas vulnerables y que la punitividad depende más del perfil psicológico del colegiado que de su trayectoria.
  > 
  > A nivel técnico, la aplicación web está construida con tecnologías nativas HTML, CSS y Javascript para maximizar el rendimiento. Se diseñó en modo oscuro con una paleta de colores de alto contraste apta para daltónicos. Las métricas éticas aplicadas aseguran la anonimización completa del colectivo arbitral.
  > 
  > Todo el código del pipeline de datos y de la web se encuentra publicado en GitHub. Muchas gracias por su atención."*

---

## 💡 Consejos para la Grabación
1. **Practica el ritmo**: No te apresures en hablar. El guion tiene unas 700 palabras, lo que permite leerlo de forma pausada y clara en 4 minutos y medio.
2. **Usa el ratón**: Acompaña tus palabras con movimientos del ratón en la pantalla. Cuando hables del mapa, pasa el cursor sobre algún punto; cuando hables de las tarjetas de veteranía, señala los valores de mediana (5,0 vs 4,0); cuando hables del scatter plot de IDP, pasa el cursor sobre algunos árbitros para mostrar la interactividad.
3. **No te detengas en detalles técnicos de código**: El evaluador valorará más ver cómo dominas y explicas la visualización y los hallazgos en la demo en vivo. Tal como indicas en tu nota, si te saltas algo pequeño, no pasa nada, ya que el profesor podrá explorar la web interactiva por su cuenta gracias al enlace público.
