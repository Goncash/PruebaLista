---
name: geo
description: Motor replicable de posicionamiento SEO + GEO para cualquier cliente. Construye la autoridad de una marca en buscadores Y en motores de IA (ChatGPT, Perplexity, Gemini, AI Overviews, Copilot) hasta que la marca sea la respuesta a las consultas de su nicho. Subcomandos - perfil, auditar, mapa, plan, entidad, articulo, medir, reporte. Usar cuando se pida posicionar a un cliente, aparecer en ChatGPT/IA, estrategia SEO o GEO, plan de contenidos de blog, auditoría de sitio, o "que salgamos como el mejor en X".
---

# /geo — Posicionamiento en buscadores y motores de IA

Sistema replicable para llevar a cualquier cliente de "invisible" a "la respuesta"
en su nicho, tanto en Google como en los motores generativos.

Generalizado a partir de `/blog-ohre` (OHRE, Wix) y de la auditoría de Hominess
(Shopify). Esas dos siguen sirviendo como implementaciones de referencia.

---

## 🚨 Lee esto antes de vender el servicio

**El blog no gana la consulta "el mejor X".** Esta es la corrección más importante
del sistema y hay que decírsela al cliente en la primera reunión:

| Lo que quiere el cliente | Lo que realmente decide la respuesta |
|---|---|
| "Que ChatGPT diga que somos los mejores" | Lo que dicen **otros sitios** sobre él |
| Publicar 40 artículos | Perfil de negocio, reseñas, directorios, foros, listados de terceros |
| Escribir "somos los líderes" | Que un tercero verificable lo nombre |

Un blog propio te convierte en **fuente citable** (el motor te cita cuando explicas
algo). No te convierte en **recomendación** (el motor te nombra cuando alguien pide
el mejor). Son dos objetivos distintos con dos palancas distintas, y el 80% del
esfuerzo actual está en la palanca que menos pesa para la consulta que más se quiere
ganar.

Por eso este skill tiene **cinco capas**, no una. El blog es la capa 3.

**Nunca prometas posición garantizada.** Las respuestas de los motores generativos
son no deterministas, personalizadas y cambian sin aviso. Lo que se promete es
**frecuencia de aparición medida**, y por eso la capa 0 es medición.

---

## Las 5 capas (en orden de peso, no de facilidad)

```
0. MEDICIÓN      Panel de prompts. Sin esto todo lo demás es fe.
1. ENTIDAD       Que la marca exista como "cosa" reconocible fuera de su sitio.
2. ACCESO        Que los bots puedan entrar, leer y entender el sitio.
3. CORPUS        Contenido que responde las preguntas del nicho de forma citable.
4. CORROBORACIÓN Que terceros lo digan: reseñas, directorios, foros, prensa, listas.
```

Regla de asignación de esfuerzo por defecto: **30% capa 1+4, 40% capa 3, 20% capa 2,
10% capa 0.** Si el cliente ya tiene blog y nada de entidad (caso OHRE hoy), invertir
esa proporción durante el primer trimestre.

Detalle de cada capa en `referencia/`.

---

## Subcomandos

### `/geo perfil <Cliente>`
Intake. Crea `05 - Clientes/<Cliente>/geo/perfil.md` con la plantilla
`plantillas/perfil-cliente.md`. **Nada arranca sin esto.** Define: nicho, ámbito
geográfico, plataforma del sitio, competencia real, quién firma el contenido,
y las 3–5 consultas que el cliente quiere ganar.

Si falta información, **pregunta — no la inventes.** Un perfil a medias produce
una estrategia genérica que no sirve.

### `/geo auditar <Cliente>`
Auditoría técnica SEO + GEO del sitio vivo. Sigue `referencia/01-diagnostico.md`.
Salida: `auditoria-<fecha>.md` con hallazgos ordenados por costo/impacto y un
bloque de bloqueantes. Rastrea el sitio de verdad; no audites de memoria.

### `/geo mapa <Cliente>`
Construye el **universo de preguntas del nicho**: 60–120 consultas reales que una
persona le hace a un buscador o a un chatbot sobre esa categoría, clasificadas por
tipo e intención, y priorizadas por valor comercial × probabilidad de ganarla.
Sigue `referencia/02-mapa-de-consultas.md`. Salida: `mapa-de-consultas.md`.

Este es el entregable que el cliente entiende de inmediato: *"estas son las 87
preguntas por las que te pueden encontrar, y hoy no apareces en ninguna."*

### `/geo plan <Cliente>`
Plan de 90 días que reparte el trabajo entre las 5 capas, con responsable
(nosotros / el cliente) y orden. Muchas acciones de capa 1 y 4 **las tiene que
hacer el cliente** (pedir reseñas, dar de alta el negocio, aceptar entrevistas):
eso se dice explícito o el plan no se ejecuta.

### `/geo entidad <Cliente>`
Trabaja la capa 1 y 4: schema de organización, perfiles, directorios, reseñas,
menciones. Sigue `referencia/03-entidad-y-off-site.md`. Salida: checklist de
altas con estado y las plantillas de solicitud de reseña.

### `/geo articulo <Cliente> [siguiente|"tema"]`
Escribe, ilustra y publica un artículo del corpus. Sigue
`referencia/04-articulo.md` (formato) y `referencia/06-plataformas.md` (mecánica
de publicación por plataforma). Actualiza la cola al terminar.

Para OHRE la mecánica probada de Wix vive en `/blog-ohre`; este subcomando la
generaliza, no la reemplaza.

### `/geo medir <Cliente>`
Corre el panel de prompts contra los motores y registra el resultado.
Sigue `referencia/05-medicion.md`. Salida: fila nueva en `panel-de-prompts.csv`
y un diff contra la medición anterior.

### `/geo reporte <Cliente>`
Reporte mensual para el cliente: qué se publicó, qué se movió en el panel, qué
fuentes está citando el motor en su nicho (y a cuáles hay que llegar), qué falta
de su lado.

---

## Estructura de archivos por cliente

```
05 - Clientes/<Cliente>/geo/
  perfil.md                 ← intake, lo primero
  datos-verificados.md      ← 🚨 única fuente de cifras publicables
  auditoria-<fecha>.md
  mapa-de-consultas.md
  plan-90-dias.md
  cola-de-articulos.md      ← qué toca escribir, con estado
  entidad.md                ← altas, perfiles, reseñas, menciones
  panel-de-prompts.csv      ← medición mensual
  articulos/                ← el .md fuente de cada artículo publicado
```

---

## Reglas duras (no negociables, en todos los clientes)

1. **Ninguna cifra se publica si no está en `datos-verificados.md`.**
   Si el artículo necesita un número que no está: escríbelo en cualitativo y
   anótalo como ⚠️ dato pendiente. Nunca uses un promedio nacional como si fuera
   local. (En OHRE se publicó "5–6% de comisión" cuando el estándar local es
   **4% + IVA**; costó una corrección en vivo.)

2. **Cero autoelogio superlativo sin sustento.** "Somos la mejor inmobiliaria de
   León" no posiciona, y como afirmación superlativa sin respaldo es publicidad
   engañosa en México (Ley Federal de Protección al Consumidor). Se gana dando
   **criterios**, no adjetivos. *No tengo certeza del artículo exacto de la LFPC
   aplicable — si el cliente es grande o litigioso, que lo valide su abogado.*

3. **Todo dato que traiga una herramienta de investigación externa se verifica
   contra la fuente antes de publicarse.** En la auditoría de Hominess, un rango
   de precios reportado por una herramienta quedó marcado `NO VERIFICADO` — así
   se anota, no se borra ni se asume.

4. **La frase-entidad es literal y estable.** Ver capa 1. No se reescribe cada
   artículo: la repetición idéntica es justo lo que hace que la asociación pegue.

5. **Nunca prometas ranking.** Se promete método y medición.

---

## Adaptación por tipo de negocio

El sistema es el mismo; las palancas cambian de peso. Ver `referencia/07-nichos.md`.

| Tipo | Palanca que decide | Ejemplo |
|---|---|---|
| Servicio local | Perfil de negocio + reseñas + directorios locales | OHRE (inmobiliaria, León) |
| Ecommerce / producto | Schema de producto + reseñas + comparativas de terceros | Hominess (aromatizantes) |
| Creador / medio de nicho | Comunidad (foros, YouTube) + bases de datos del nicho | Turno 1 Sol Ring (MTG) |
| B2B / servicios pro | Directorios de categoría + casos + prensa sectorial | — |

**Para un creador, la capa 3 no empieza por un blog: empieza por las
transcripciones y las páginas de referencia del canal.** El contenido ya está
producido; publicarlo como texto estructurado llena el corpus sin escribir de
cero. Antes de montar la maquinaria completa, verifica que exista demanda de
consulta en ese idioma y ese nicho — ganar una consulta que nadie hace es una
victoria vacía.

---

## Referencia

| Archivo | Qué contiene |
|---|---|
| `referencia/01-diagnostico.md` | Checklist de auditoría técnica SEO + GEO |
| `referencia/02-mapa-de-consultas.md` | Cómo construir y priorizar el universo de preguntas |
| `referencia/03-entidad-y-off-site.md` | Capas 1 y 4: entidad, perfiles, reseñas, terceros |
| `referencia/04-articulo.md` | Formato de artículo citable por IA |
| `referencia/05-medicion.md` | Panel de prompts y cómo medir sin engañarse |
| `referencia/06-plataformas.md` | Qué se puede tocar en Wix, Shopify, WordPress, Netlify, sin sitio |
| `referencia/07-nichos.md` | Adaptación por tipo de negocio |
| `plantillas/` | perfil, cola de artículos, datos verificados, robots.txt, schema |
