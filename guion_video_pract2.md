# Guion Video — PRACT2 Visualización de Datos (UOC)
**Joan Mata Parraga · Máx. 5 minutos**

---

## INTRO (aprox. 15 seg.)

Hola, soy Joan Mata, árbitro de fútbol en activo y estudiante del máster en Data Science de la UOC. Este proyecto combina mis dos mundos: el arbitraje y el análisis de datos. Lo que os voy a mostrar hoy es un dashboard interactivo que analiza si el entorno socioeconómico del barrio donde se juega un partido influye en la conflictividad del juego y en cómo el comité de designación gestiona esa situación.

---

## EXPLORACIÓN INICIAL (aprox. 30 seg.)

[mostrar sección "Exploración" del dashboard]

El proyecto parte de tres preguntas concretas. Primera: ¿las zonas con mayor exclusión social —medida por el índice IST del Idescat— generan más tarjetas en los partidos? Segunda: ¿el comité de designación responde enviando árbitros más veteranos a esas zonas de mayor riesgo? Y tercera: ¿tiene el propio árbitro un estilo punitivo propio e independiente de su experiencia?

Para responderlas he cruzado las actas de la Federació Catalana de Futbol de la temporada 25/26 —más de 44.000 partidos y 2.110 árbitros— con los índices socioeconómicos territoriales del Idescat de 2023.

---

## ACTO 1 — Entorno Socioeconómico y Conflictividad (aprox. 60 seg.)

[mostrar sección "Acto 1" con el mapa activo]

Aquí tenemos el mapa interactivo. Cada círculo es un territorio —un barrio o municipio de Cataluña— y el color nos dice su nivel socioeconómico: en rojo los territorios con un IST bajo, es decir, más vulnerables; en azul los de IST alto, más acomodados. El tamaño del círculo refleja el volumen de partidos jugados.

[desplazar el mapa, hacer clic en un punto rojo de baja renta]

Si hago clic en una zona de IST bajo, como por ejemplo este territorio del área metropolitana, vemos en el panel lateral su IST, la media de tarjetas por partido y los campos locales.

[desplazarse al scatter plot debajo del mapa]

Y aquí está la clave: el scatter plot. Cada punto es un territorio. La recta roja es la línea de regresión. ¿Qué vemos? La relación existe, pero es débil. En la categoría Cadete, las zonas con IST bajo registran un 1,5% más de tarjetas que las de IST alto. Pero en Juvenil y Amateur la tendencia prácticamente desaparece o se invierte. Conclusión: el IST influye, pero no es el factor determinante. La conflictividad depende de muchas más variables.

---

## ACTO 2 — Gestión Institucional del Riesgo (aprox. 60 seg.)

[desplazarse a la sección "Acto 2" con los boxplots]

Ahora la segunda pregunta: ¿el comité de designación actúa de forma estratégica? Aquí vemos tres tarjetas con estadísticas de distribución de veteranía de los árbitros, agrupadas por nivel de IST de la zona del partido: Bajo IST en rojo, Medio en naranja, Alto en azul.

[señalar los valores de mediana]

La mediana de años de experiencia en zonas de IST bajo es de 5,0 años. En zonas de IST alto, baja a 4,0 años. La media también lo confirma: 6,3 años frente a 6,1 años. La diferencia no es enorme, pero es estadísticamente consistente. Parece que hay una tendencia a enviar árbitros algo más curtidos a los entornos más complicados. No es una política sistemática escrita en ningún reglamento, pero los datos la sugieren.

[pausa, señalar los percentiles Q1 y Q3]

Fijémonos también en los cuartiles: en todos los grupos el rango intercuartílico va de unos 3 a 8 años, lo que indica una distribución similar en todos los niveles de IST. La diferencia está en la tendencia central, no en la dispersión.

---

## ACTO 3 — El Factor Humano: IDP vs Experiencia (aprox. 60 seg.)

[desplazarse a la sección "Acto 3" con el scatter de árbitros]

Y ahora el hallazgo más interesante para mí, que soy árbitro. Aquí cada punto es un árbitro. El eje X es su veteranía en años, el eje Y es su IDP —Índice de Desviación de Punitividad— que mide cuántas tarjetas saca de media por encima o por debajo de la media de su categoría. El color identifica su rango FCA: desde gris para los cursetistas noveles hasta rojo para los árbitros de tercera federal o nacional.

[hacer clic en diferentes puntos del scatter]

Si el IDP dependiera de la experiencia, esperaríamos ver una tendencia clara: árbitros con más años más arriba o más abajo. Pero no la hay. La nube de puntos es prácticamente vertical en todos los rangos. La mediana global del IDP es de +0,94 tarjetas, lo que significa que la mayoría saca algo más que la media de su categoría —un leve sesgo hacia lo estricto— pero esa magnitud no cambia con los años.

[señalar un cursetista y un árbitro de élite con IDP parecido]

Mira: este cursetista con 1 año de experiencia y este árbitro de primera categoría con 15 años tienen IDPs muy similares. El estilo punitivo es una característica individual y estable, que no se corrige simplemente acumulando partidos.

---

## CONCLUSIONES (aprox. 30 seg.)

[desplazarse a la sección de Conclusiones]

Resumiendo los tres hallazgos. Primero: el IST tiene una influencia débil y no uniforme sobre la conflictividad; en Cadete algo más visible, en otras categorías prácticamente nula. Segundo: las designaciones sí muestran una tendencia estadística a asignar árbitros más veteranos a zonas de menor IST, aunque no es una diferencia drástica. Y tercero: el IDP, el estilo punitivo de cada árbitro, es una característica individual estable que no depende del rango FCA ni de los años de experiencia.

---

## CIERRE (aprox. 15 seg.)

[mostrar el footer de la web con enlaces a GitHub y joanmata.com]

Los datos provienen de las actas oficiales de la FCF temporada 25/26 y del índice IST del Idescat 2023. En cuanto a la privacidad: los NIF de los árbitros se eliminaron en el preprocesamiento y todos los nombres están anonimizados bajo el formato COL_XXXX. El código y los datos están publicados en GitHub y el dashboard está disponible públicamente en joanmata.com/VD/PRACT. Muchas gracias.

---

*Duración estimada total: aprox. 4 min 35 seg.*
