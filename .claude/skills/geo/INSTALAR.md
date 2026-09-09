# Cómo instalar este skill

Este repositorio (`PruebaLista`) **no es el hogar de tus skills** — es donde se
desarrolló. Para usarlo:

1. Copia la carpeta `geo/` completa a tu directorio de skills:
   `C:\...\.claude\skills\geo\`
   (el mismo sitio donde viven `contenido`, `estrategia`, `pauta`, `blog-ohre`).
2. Reinicia Claude Code. El skill se invoca con `/geo`.
3. Añádelo a la tabla de skills del `MANUAL.md`:

   | `/geo` | Posicionamiento SEO/GEO: `perfil` · `auditar` · `mapa` · `plan` · `entidad` · `articulo` · `medir` · `reporte` |

## Relación con `/blog-ohre`

`/blog-ohre` sigue siendo válido y **no se toca**: es la implementación
específica de OHRE en Wix, con la mecánica de publicación ya probada.
`/geo` es el sistema general del que `/blog-ohre` es una instancia.

Orden recomendado:
- Cliente nuevo → `/geo`
- Escribir un artículo de OHRE → `/blog-ohre` (más específico, ya funciona)

Si algún día quieres unificarlos, la ruta es mover la mecánica de Wix de
`/blog-ohre` a `referencia/06-plataformas.md` y dejar solo `/geo`. No lo hagas
hasta que `/geo` esté probado en al menos dos clientes.

## Qué NO hace este skill todavía

- No corre el panel de medición automáticamente. `/geo medir` describe el método;
  ejecutarlo requiere consultar los motores manualmente o contratar una plataforma.
- No tiene datos de volumen de búsqueda. Sin una fuente de datos de palabras clave,
  el mapa de consultas es una propuesta de arquitectura, no una medición.
- No incluye la mecánica de publicación de WordPress ni de sitios estáticos: solo
  está documentada la de Wix (probada) y la de Shopify (auditada).
