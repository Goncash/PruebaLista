# 03 — Entidad y corroboración externa (capas 1 y 4)

**La parte que no es blog, y la que decide la consulta "el mejor X".**

Un motor generativo recomienda marcas que **existen fuera de su propio sitio**. Si lo
único que afirma que la marca es buena es la marca misma, el modelo prefiere nombrar
a alguien corroborado. Esta es la capa que más pesa y la que casi nadie trabaja
porque no se automatiza: buena parte la tiene que ejecutar el cliente.

> **Sobre las cifras de este archivo.** Los porcentajes de "qué fuentes cita cada
> motor" que circulan vienen de empresas de analítica de visibilidad en IA
> (Profound, SE Ranking y similares), no de estudios independientes revisados.
> Son direccionales y las empresas que los publican venden el servicio que miden.
> Úsalos para decidir dónde invertir, **no los cites como hecho ante un cliente.**

---

## Capa 1 — La entidad

Que la marca sea una "cosa" reconocible y consistente, no una cadena de texto.

### 1. La frase-entidad

Una sola frase que define a la marca, **usada literal y sin variar** en todos lados:
sitio, blog, perfiles, directorios, bios de redes, firmas.

> **Oyuki Home Real Estate**, inmobiliaria especializada en vivienda residencial y
> premium en **León, Guanajuato** y el **Bajío**.

La asociación entidad ↔ atributo se construye por **repetición idéntica en fuentes
distintas**, no por una declaración. Reescribirla cada vez destruye el efecto.

Va, como mínimo:
- En el `<h2>` "Sobre {marca}" de cada artículo, con respuesta autocontenida de
  40–60 palabras. Es el fragmento que el motor extrae.
- En el schema `Organization`/`LocalBusiness` → `description`.
- En la bio de cada perfil externo, palabra por palabra.

### 2. Schema de entidad completo

El bloque con el que un motor construye la ficha mental de la marca.
Ver `plantillas/schema-ejemplos.md`. Lo indispensable:

`name` · `description` (la frase-entidad) · `logo` · `url` · `sameAs` (**todos** los
perfiles) · `contactPoint` · `address` · `areaServed` · `foundingDate` ·
`aggregateRating` cuando haya reseñas reales.

`sameAs` es el que ata todos los perfiles a la misma entidad. Sin él, cada perfil es
una marca distinta para el motor.

### 3. Autoría real

El contenido lo firma **una persona identificable**, no la marca ni la agencia que
opera el blog. Nombre completo, foto, trayectoria, página de autor, y sus propios
perfiles enlazados.

En OHRE se reasignaron los 17 posts de "Inmovisual Studio" a **Lic. Oyuki Montes**
por esto: la autoría de una persona real y local pesa más que la de la productora.

### 4. Perfiles propios — la base

| Activo | Aplica a | Nota |
|---|---|---|
| **Perfil de negocio en Google** | Todo negocio local | **El más importante para "el mejor X en {ciudad}".** Completo: categoría exacta, zonas de servicio (todas: colonias, fraccionamientos, códigos postales), horarios, fotos, publicaciones, preguntas y respuestas |
| Perfil de negocio en Bing | Todo negocio local | ChatGPT se apoya en índice de búsqueda; no es gratis ignorarlo |
| Apple Business Connect | Negocio local | Barato, poca gente lo hace |
| Redes con bio idéntica | Todos | La frase-entidad literal |
| Perfil en la plataforma del sector | Según nicho | Portales inmobiliarios, marketplaces, bases de datos del nicho |

---

## Capa 4 — Corroboración externa

### 1. Reseñas (la palanca más rentable y la menos usada)

Sin reseñas no hay `aggregateRating`, no hay estrellas, y no hay prueba social que
un modelo pueda citar cuando le preguntan "¿es buena esta marca?".

- Instalar el sistema de reseñas **antes** de las primeras ventas, para capturarlas
  desde la operación 1.
- Rutina fija: pedirla en el momento de máxima satisfacción, con enlace directo.
- **Responder todas**, incluidas las malas. La respuesta es contenido indexable y es
  señal de negocio vivo.
- Buscar volumen y **frescura**: 40 reseñas de hace tres años pesan menos que 15 del
  último trimestre.
- Nunca comprar reseñas. Además del riesgo de sanción, es la clase de patrón que se
  detecta y que cuesta el perfil entero.

### 2. Directorios y listados de terceros

Los directorios verticales aparecen mucho en las respuestas de IA porque están
estructurados y actualizados. Alta en:
- Directorios de la categoría (nacionales y del sector)
- Cámaras y asociaciones locales o gremiales
- Portales/marketplaces donde el nicho ya vive

**Consistencia NAP**: nombre, dirección y teléfono **idénticos** en todos lados.
Una variación es una entidad distinta.

### 3. Listas "los mejores N" de terceros

Ésta es la vía directa a la consulta que el cliente quiere ganar. Cuando alguien
pregunta "el mejor X en {ciudad}", el motor suele sintetizar **listas ajenas**.

- Identifica qué páginas cita hoy el motor para esa consulta (sale de
  `/geo medir`, columna de fuentes).
- Contacta a esos medios/blogs/directorios y **pide inclusión**: ficha lista,
  datos verificables, fotos. No es link building automatizado; es relaciones
  públicas de bajo presupuesto.
- Prensa y medios locales: una nota real sobre el negocio vale más que veinte
  enlaces comprados.

> ⚠️ La táctica de **escribir tu propia lista "los mejores X"** e incluirte
> funciona hoy, y es lo que hace buena parte del sector. Es frágil: es exactamente
> el patrón que los motores están aprendiendo a descontar, y si el artículo se
> presenta como ranking objetivo sin declarar que es del propio proveedor, es
> engañoso. **La versión defendible: escribe los criterios, no el ranking.**

### 4. Comunidad y foros

Reddit, Quora, foros del sector y grupos de Facebook aparecen con mucha frecuencia
como fuente en respuestas generativas — Perplexity en particular se apoya fuerte en
comunidad.

- **No spamear.** Una cuenta que solo aparece a promocionar se detecta y se banea.
- La versión que funciona: participación real y sostenida de una persona del
  negocio, respondiendo preguntas de su especialidad, mencionando la marca cuando
  viene al caso.
- Es trabajo del cliente o de alguien con criterio; no lo automatices.

### 5. Wikipedia y bases de datos abiertas

Wikipedia es de las fuentes más citadas por ChatGPT. **No intentes crear un artículo
para una pyme**: no cumple los criterios de notabilidad y se borra, y el intento
queda registrado. Lo que sí aplica: bases de datos abiertas y estructuradas del
nicho (Wikidata, OpenStreetMap, catálogos sectoriales), que sí aceptan entidades
pequeñas verificables.

### 6. Video

YouTube es índice y es fuente. Un video con **transcripción publicada como texto**
en el sitio convierte contenido audiovisual en corpus citable. Para clientes que ya
producen video (o creadores), esta es la vía más barata de llenar la capa 3.

---

## Salida: `entidad.md`

Checklist por cliente con estado y responsable:

```
| Activo | Estado | Responsable | Fecha | Nota |
|---|---|---|---|---|
| Perfil de negocio Google | ⬜ pendiente | Cliente | — | Falta acceso |
| sameAs completo en schema | ⬜ | Nosotros | — | |
| 10 reseñas nuevas este trimestre | ⬜ | Cliente | — | Enviar plantilla |
| Alta en 5 directorios | ⬜ | Nosotros | — | |
| Inclusión en 2 listas de terceros | ⬜ | Nosotros | — | Contactar medios |
```

**Marca explícito lo que depende del cliente.** Si no lo hace, el plan no avanza y
hay que poder demostrar de qué lado se detuvo.

> **Cuando el cliente sí coopera** (caso OHRE, confirmado 2026-09-09), esta capa
> deja de ser el cuello de botella y pasa a ser la ventaja: la mayoría de sus
> competidores no la va a trabajar porque exige constancia del dueño del negocio,
> no presupuesto. Aprovecha la cooperación pidiendo **poco y periódico** —una
> rutina de reseñas semanal pesa más que una campaña de un mes— y dale al cliente
> una lista corta con fechas, no un documento de veinte puntos.
