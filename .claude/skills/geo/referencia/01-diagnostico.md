# 01 — Auditoría técnica SEO + GEO

Método probado en hominess.mx (Shopify, 23 URLs) y aplicable a cualquier sitio.
**Rastrea el sitio vivo.** No audites de memoria ni desde el panel del CMS: lo que
importa es lo que el bot recibe.

## Antes de empezar

- Si el sitio está tras contraseña o en "próximamente", **ese es el hallazgo #0** y
  manda sobre todos los demás. El primer rastreo después de abrirlo fija la línea
  base que Google archiva y que los modelos absorben. Se arregla antes, no después.
- Anota el alcance y lo que **no** pudiste medir (ej. Core Web Vitals de campo si el
  sitio no es público). Un límite declarado vale más que un número inventado.

## Qué se rastrea

```
/robots.txt          /sitemap.xml         /llms.txt
/agents.md           /.well-known/*       todas las URLs del sitemap
```

Para cada URL: código de respuesta, `<title>`, meta description, H1/H2/H3, conteo de
palabras, imágenes con y sin `alt`, enlaces internos entrantes, JSON-LD, peso del
HTML, número de scripts.

---

## A. SEO técnico

- [ ] **Títulos.** ¿Cada `<title>` contiene la palabra por la que esa página debería
      salir? El error caro y barato: plantillas tipo `{nombre} – MARCA` sin keyword.
      60 caracteres útiles; no repitas la marca dos veces.
- [ ] **Meta descriptions.** ¿Faltan? ¿Alguna publica texto de trabajo
      ("Pendiente descripción")? Rango útil 140–160.
- [ ] **Canibalización.** URLs distintas sirviendo el mismo contenido. Elegir la
      canónica; borrar o excluir del sitemap las demás (incluida la basura de demo
      del tema).
- [ ] **Páginas huérfanas.** Páginas importantes sin un solo enlace interno entrante.
      Están en el sitemap pero con cero autoridad interna.
- [ ] **Enlaces rotos** internos (404).
- [ ] **Encabezados.** Un solo H1 por página, y que describa qué se vende. Ojo con el
      ruido: carritos, buscadores y modales usando `<h2>` como estilo ensucian el
      esquema para el rastreador y para lectores de pantalla.
- [ ] **Breadcrumbs** visibles y en schema.
- [ ] **`hreflang`** si hay más de un idioma o mercado.
- [ ] **`og:image`** por https (no http), tamaño correcto.
- [ ] **Peso y velocidad.** HTML por página, número de scripts externos, hojas de
      estilo. Medir PageSpeed / Core Web Vitals cuando el sitio sea accesible.
- [ ] **Renderizado.** Si el contenido solo aparece con JavaScript, muchos bots de IA
      **no lo ven**. Comprueba con `curl` sin JS qué texto llega. Este punto es
      específico de GEO y se salta en las auditorías SEO tradicionales.

## B. Imágenes

- [ ] Fotos reales y **distintas por producto/propiedad**. Repetir la misma imagen (o
      peor, la misma imagen generada por IA) en todo el catálogo destruye la
      diferenciación y la confianza.
- [ ] `alt` descriptivo con keyword y contexto local. Regla:
      `{Producto} — {qué es}, {atributo}, {lugar}`.
- [ ] Nombres de archivo con significado, no `IMG_2043` ni `Gemini_Generated_Image_…`.

## C. Datos estructurados (Schema.org)

Es el bloque con el que un motor de IA **construye la entidad**. Verifica que exista
y esté completo, no solo que exista.

- [ ] `Organization` o `LocalBusiness` completo: `name`, `logo`, `description`,
      `url`, `sameAs` (todas las redes y perfiles), `contactPoint`, `address`,
      `foundingDate`, `areaServed`. Un `Organization` con solo nombre y URL es un
      hueco, no un acierto.
- [ ] Schema específico del tipo de negocio: `RealEstateAgent`, `Product` /
      `ProductGroup`, `Service`, `VideoObject`, etc.
- [ ] `aggregateRating` y `review` — lo que activa estrellas y lo que un LLM lee para
      decidir si te recomienda. Requiere reseñas reales; no se inventan.
- [ ] `FAQPage` donde ya haya preguntas y respuestas escritas. Es habitual encontrar
      FAQ escritas y sin marcar: son resultados enriquecidos regalados.
      *Nota: Google restringió los rich snippets de FAQ en 2023 para la mayoría de
      sitios. El marcado sigue sirviendo para comprensión y para IA, pero no lo
      vendas como "vas a salir con acordeón en Google".*
- [ ] `WebSite` + `SearchAction`, `BreadcrumbList`, `Article` con `author` y fechas.

## D. Contenido y E-E-A-T

- [ ] **Texto de trabajo publicado.** Buscar "pendiente", "lorem", "TODO", "por
      definir". Es lo peor que puede leer un motor de IA: o lo cita textual o te
      descarta como fuente poco fiable.
- [ ] **Contradicciones internas.** Dos respuestas opuestas a la misma pregunta en el
      mismo dominio es motivo directo para no citar la fuente.
- [ ] **Autoría real.** Persona identificable con nombre, foto y trayectoria, no una
      marca genérica ni "el equipo". Pesa para E-E-A-T y para IA.
- [ ] **Página "quiénes somos"** con quién está detrás, desde cuándo, dónde opera.
- [ ] **Volumen editorial vs. competencia.** Cuenta artículos en el sitemap de blog de
      los 4–6 competidores reales. Es el dato que más mueve al cliente.
- [ ] **Reseñas.** Cero reseñas = cero prueba social citable.

## E. GEO — acceso y citabilidad

- [ ] **`robots.txt` y bots de IA.** Ver `plantillas/robots.txt`. Comprobar si algún
      bot está bloqueado por accidente (o por el CMS). Y confirmar con el cliente que
      permitir el rastreo de IA es **una decisión, no un descuido**.
- [ ] **`llms.txt`.** Existe pero su valor está en duda (ver `05-medicion.md`). Si el
      CMS lo genera con una plantilla genérica, sustituirlo por uno propio cuesta poco.
      No lo vendas como la palanca.
- [ ] **Formato citable.** El material bueno suele existir ya, escondido en acordeones
      sin la pregunta como encabezado. Un pasaje citable dentro de una ficha de
      producto compite con el botón de comprar; el mismo pasaje en un artículo
      titulado con la pregunta se cita solo.
- [ ] **Corroboración externa.** ¿La marca existe fuera de su dominio? Sin `sameAs`,
      sin perfil de negocio, sin menciones ni reseñas, lo que diga el sitio no tiene
      con qué contrastarse — y el modelo prefiere nombrar a un competidor.

---

## Salida

`auditoria-<fecha>.md` con:

1. **Hallazgo #0** — el que manda sobre todos los demás, si existe.
2. Secciones A–E con evidencia (tablas con la URL y el valor real encontrado).
3. **Plan de acción en tres bloques**: 🔴 bloqueantes · 🟠 semana 1 · 🟡 mes 1–3.
4. **Resumen en una línea** — la frase que el cliente va a repetir.
5. Dónde quedaron los datos crudos del rastreo.
