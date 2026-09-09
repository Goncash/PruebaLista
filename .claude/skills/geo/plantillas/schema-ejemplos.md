# Plantillas de datos estructurados (JSON-LD)

> Valida siempre con el validador de schema.org y con la herramienta de resultados
> enriquecidos de Google antes de dar por buena una implementación.
>
> Estos bloques son con lo que un motor de IA **construye la entidad**. Un
> `Organization` con solo `name` y `url` no es un acierto: es un hueco.

## Organización / negocio local

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://EJEMPLO.com/#organizacion",
  "name": "{Nombre exacto y consistente}",
  "description": "{La frase-entidad, literal}",
  "url": "https://EJEMPLO.com",
  "logo": "https://EJEMPLO.com/logo.png",
  "image": "https://EJEMPLO.com/foto.jpg",
  "telephone": "+52...",
  "email": "hola@EJEMPLO.com",
  "foundingDate": "20XX",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "",
    "addressLocality": "León",
    "addressRegion": "Guanajuato",
    "postalCode": "",
    "addressCountry": "MX"
  },
  "areaServed": [
    { "@type": "City", "name": "León" },
    { "@type": "City", "name": "Silao" }
  ],
  "sameAs": [
    "https://www.instagram.com/...",
    "https://www.facebook.com/...",
    "https://www.youtube.com/@...",
    "https://maps.google.com/..."
  ],
  "contactPoint": [{
    "@type": "ContactPoint",
    "telephone": "+52...",
    "contactType": "ventas",
    "availableLanguage": ["es", "en"]
  }]
}
```

`sameAs` es el que ata todos los perfiles a la misma entidad. Sin él, cada perfil
es una marca distinta para el motor. Inclúyelos **todos**.

Tipos más específicos según el negocio: `RealEstateAgent`, `Restaurant`,
`ProfessionalService`, `Store`. Usa el más específico que aplique.

## Artículo con autor real

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{Título, ≤110 caracteres}",
  "description": "{Meta description}",
  "image": "https://EJEMPLO.com/portada.jpg",
  "datePublished": "2026-09-09",
  "dateModified": "2026-09-09",
  "author": {
    "@type": "Person",
    "name": "{Nombre real}",
    "jobTitle": "{Cargo}",
    "url": "https://EJEMPLO.com/autor/{slug}",
    "sameAs": ["https://www.linkedin.com/in/..."]
  },
  "publisher": { "@id": "https://EJEMPLO.com/#organizacion" },
  "inLanguage": "es-MX"
}
```

El `author` como `Person` con `sameAs` propio es señal de E-E-A-T. Firmar con la
marca o con la agencia desperdicia la señal.

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "{La pregunta, literal como la teclea una persona}",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "{Respuesta autocontenida de 40–60 palabras, con el sujeto completo}"
    }
  }]
}
```

> Google restringió en 2023 los resultados enriquecidos de FAQ para la mayoría de
> sitios. El marcado sigue sirviendo para comprensión y para motores de IA, pero
> **no lo vendas como "vas a salir con acordeón en Google"**.

## Producto con reseñas

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{Producto}",
  "image": ["https://EJEMPLO.com/producto-1.jpg"],
  "description": "{Descripción real, no una línea}",
  "brand": { "@type": "Brand", "name": "{Marca}" },
  "sku": "",
  "offers": {
    "@type": "Offer",
    "price": "150.00",
    "priceCurrency": "MXN",
    "availability": "https://schema.org/InStock",
    "url": "https://EJEMPLO.com/producto"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "37"
  }
}
```

⚠️ `aggregateRating` y `review` **solo con reseñas reales**. Inventarlas es motivo
de sanción manual y, cuando se descubre, cuesta el perfil entero.

## Breadcrumbs, sitio y video

`BreadcrumbList` (jerarquía), `WebSite` + `SearchAction` (caja de búsqueda de sitio)
y `VideoObject` con `transcript` para clientes con canal de video. Este último es la
forma de que el contenido audiovisual entre al corpus citable.
