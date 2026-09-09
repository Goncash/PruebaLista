# 06 — Qué se puede tocar en cada plataforma

Antes de prometer nada, confirma en qué está montado el sitio. La mitad de las
recomendaciones de una auditoría genérica son imposibles en el CMS del cliente.

## Wix — caso OHRE

- **Blog por API.** `POST /blog/v3/draft-posts` → `publish`. Contenido en formato
  Ricos (no HTML). El autor es un `memberId` del sitio.
- ⚠️ El sandbox de `ExecuteWixAPI` **bloquea todo `fetch` externo** (solo APIs de
  Wix). El contenido va incrustado en el código, nunca descargado de una URL.
  Las imágenes se suben con `UploadImageToWixSite`, no con `ExecuteWixAPI`.
- Imágenes desde el Media Manager: `GET /site-media/v1/files?mediaTypes=IMAGE`,
  paginando con `paging.cursor` desde `res.nextCursor.cursors.next` (**no**
  `paging.offset`).
- `seoData.tags` para título y meta. `excerpt` = meta description (≤155).
- `FAQPage` se genera solo desde un H2 con el texto exacto `Preguntas frecuentes`.
- Reasignar autoría de posts publicados: `PATCH /blog/v3/draft-posts/update`, máx.
  20 por lote, `action: "UPDATE_PUBLISH"`. Conserva slug y fecha de primera
  publicación.
- Limitaciones: control fino de `robots.txt` y de schema personalizado es limitado
  según el plan. Verificar antes de prometerlo.

La mecánica completa y probada está en la skill `/blog-ohre`.

## Shopify — caso Hominess

- Trae de fábrica `robots.txt`, `sitemap.xml`, `llms.txt`, `agents.md`,
  `/.well-known/ucp` y endpoint MCP de catálogo: **la tienda ya habla el protocolo
  de agentes sin trabajo adicional.** Es un diferenciador real frente a quien solo
  vende por marketplace, y vale la pena decírselo al cliente.
- Pero `llms.txt` y `agents.md` son **la plantilla genérica de Shopify**, palabra
  por palabra. Sustituirlos por uno propio de marca es trabajo de media hora.
- Schema `ProductGroup` automático y bastante completo; suele faltarle
  `productGroupID`, `variesBy`, `gtin`/`mpn`, `hasMerchantReturnPolicy`,
  `shippingDetails` y **`aggregateRating`/`review`**.
- `Organization` sale casi vacío (nombre + URL). Hay que completarlo a mano.
- `product_type` y `tags` suelen estar sin usar: sin ellos no hay navegación por
  facetas y los feeds salen con la categoría genérica.
- Títulos y metas: plantilla en el tema + campo SEO por ficha.

## WordPress

La plataforma con más control. Schema, `robots.txt`, redirecciones, plantillas de
título y contenido: todo tocable. Si el cliente puede elegir, es la opción que menos
límites impone. Cuidado con la acumulación de plugins de SEO en conflicto.

## Netlify / sitio estático

Control total del `robots.txt`, cabeceras, `sitemap.xml` y JSON-LD, pero el blog hay
que montarlo (CMS headless o archivos en el repo). Ventaja de GEO: HTML servido sin
depender de JavaScript, que es exactamente lo que un bot lee mejor.

⚠️ **Renderizado por JavaScript.** En cualquier stack tipo SPA, comprueba con
`curl` qué texto llega sin ejecutar JS. Varios bots de IA no ejecutan JavaScript: si
el contenido no está en el HTML inicial, para ellos no existe.

## Sin sitio propio (creadores, canales)

No hay capa 3 que optimizar hasta que exista dónde publicar. Opciones, de menos a
más trabajo:

1. **Descripciones y transcripciones** de los videos, bien escritas, en la
   plataforma que ya usa. Es texto indexable.
2. Un sitio estático mínimo con la biblioteca de transcripciones y páginas de
   referencia del nicho. Barato y suficiente para empezar a ser fuente.
3. Sitio completo con blog.

**No vendas la maquinaria completa a un cliente que aún no tiene dónde publicarla.**
