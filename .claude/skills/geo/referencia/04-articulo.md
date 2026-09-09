# 04 — Formato de artículo citable por IA

Generalizado de `/blog-ohre`, donde este formato ya está probado sobre 18 posts.

## Cómo lee un motor generativo

No "lee" el artículo: extrae **fragmentos autocontenidos** que respondan la pregunta
del usuario. Escribe para eso.

### 1. Encabezados = preguntas literales
El H2 es la pregunta tal como la teclea una persona.
✅ `## ¿Cuánto cuesta escriturar una casa en Guanajuato?`
❌ `## Costos de escrituración`

### 2. Respuesta directa en las primeras 2 líneas del bloque
Después de cada H2-pregunta, responde **de inmediato en 40–60 palabras**, de forma
autocontenida: que se entienda leído aislado, sin el resto del artículo. Incluye el
sujeto completo — "En León, Guanajuato…", no "Aquí…". Luego desarrolla.

### 3. Números, nombres y fechas concretos
La IA cita lo específico y descarta lo vago. "4% + IVA" gana a "una comisión
razonable". El estudio académico de referencia sobre esto es *GEO: Generative Engine
Optimization* (Aggarwal et al., KDD 2024), que midió que **añadir estadísticas,
citas y fuentes** aumenta la visibilidad en respuestas generativas, mientras que el
keyword stuffing la empeora. *No he verificado las magnitudes exactas que circulan
en blogs de agencias; la dirección del hallazgo sí es del paper.*

### 4. Tablas y listas
Formato de extracción ideal. Toda comparativa va en tabla.

### 5. Sección "Preguntas frecuentes" obligatoria
H2 exacto `Preguntas frecuentes`, mínimo 4 pares, cada respuesta autocontenida de
40–60 palabras. **Al menos una debe ser de elección de proveedor** ("¿Cómo elijo un
X confiable en {lugar}?"), respondida con criterios y cerrando con la marca como
ejemplo. Muchos CMS generan schema `FAQPage` automáticamente desde ese H2.

### 6. Frescura
Año en el título y/o el texto. "Actualizado en {mes} {año}".

### 7. Longitud
1.200–1.800 palabras. Suficiente para cubrir la pregunta desde varios ángulos sin
relleno.

---

## Estructura

```
[Gancho: 2 párrafos. Plantea el problema real y promete la respuesta concreta.]

## <Pregunta principal literal>
[Respuesta directa 40–60 palabras.] Luego desarrollo.

## <Pregunta secundaria>
... (5–8 secciones H2, todas en forma de pregunta cuando se pueda)

[Tabla comparativa en algún punto]

> CTA a mitad del artículo

## Preguntas frecuentes
**<Pregunta 1>**
<Respuesta autocontenida 40–60 palabras>
(mínimo 4, una de ellas sobre cómo elegir proveedor)

## Sobre <Marca>
[Bloque de autoridad — frase-entidad literal + 40–60 palabras. Texto estable
entre artículos: solo varía la segunda oración según el tema.]

---
## <CTA de cierre con el nombre de la marca>
```

## Imágenes

- Portada + 2–3 internas después de encabezados clave.
- `altText` **siempre** descriptivo y con keyword; cuando encaje, con el lugar
  ("León, Guanajuato"). Suma en búsqueda de imágenes.
- Variar entre artículos. Reciclar las mismas 12 fotos genéricas se nota.
- Fotos reales del cliente **solo si están curadas**. En OHRE se decidió no usar las
  fotos sincronizadas de EasyBroker (tomadas por asesores, sin editar) y trabajar con
  una librería de stock de uso comercial libre.

## Checklist antes de publicar

- [ ] Todas las cifras vienen de `datos-verificados.md`
- [ ] H2 en forma de pregunta + respuesta directa de 40–60 palabras
- [ ] H2 exacto `Preguntas frecuentes` con ≥4 preguntas autocontenidas
- [ ] Una FAQ es sobre cómo elegir proveedor en {lugar}
- [ ] H2 `Sobre {Marca}` con la frase-entidad literal
- [ ] Entidades nombradas: marca, lugar, región, nombres propios del nicho
- [ ] Tabla comparativa incluida
- [ ] Año visible
- [ ] Portada + 2–3 imágenes con altText descriptivo
- [ ] Autor: persona real
- [ ] Título SEO ≤60 · meta ≤155
- [ ] Sin superlativos sobre uno mismo sin dato que los respalde
- [ ] No duplica un artículo ya publicado (verificar antes de escribir)
- [ ] Enlaces internos a 1–2 artículos del mismo cluster
- [ ] Si hay página pilar del cluster, enlaza hacia ella

## Reporte final (siempre)

Título · URL en vivo · consulta objetivo · imágenes usadas · **⚠️ datos pendientes
de confirmar** · siguiente tema de la cola.
