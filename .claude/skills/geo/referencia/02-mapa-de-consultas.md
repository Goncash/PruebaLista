# 02 — Mapa de consultas del nicho

El entregable que el cliente entiende de inmediato:
*"Estas son las 87 preguntas por las que te pueden encontrar. Hoy no apareces en
ninguna. Vamos a ir por ellas en este orden."*

## Principio

**No son "temas de blog": son consultas.** El título de cada pieza es la pregunta
tal como la teclea o la dicta una persona. Eso es lo que hace que un motor
generativo la empareje con la pregunta del usuario y cite la fuente.

❌ "Costos de escrituración"
✅ "¿Cuánto cuesta escriturar una casa en Guanajuato?"

## Las 8 familias de consulta

Cruza cada una con el nicho del cliente hasta agotar. Objetivo: **60–120 consultas**.

| Familia | Forma típica | Valor comercial |
|---|---|---|
| **Categoría** | "¿qué es X?" · "¿cómo funciona X?" | Bajo, pero define la categoría antes que la competencia |
| **Dinero** | "¿cuánto cuesta X?" · "¿cuánto necesito para X?" | Alto volumen. Las preguntas de dinero siempre lideran |
| **Comparación** | "X vs Y" · "¿cuál conviene?" | Alto. Intención de decisión |
| **Elección de proveedor** | "el mejor X en {lugar}" · "cómo elegir X" · "¿es confiable X?" | **El más alto.** Es la consulta que trae cliente |
| **Contexto local / temporal** | "X en {ciudad}" · "X en 2026" | Alto si el negocio es local |
| **Miedo** | "riesgos de X" · "focos rojos" · "cómo evitar que me estafen" | Altísima conversión |
| **Proceso** | "cómo hacer X paso a paso" · "qué documentos necesito" | Medio. Construye autoridad |
| **Recomendación** | "los mejores N X" · "mejores X para {caso}" | Alto. Formato lista, muy citable |

## Cómo se construye

1. **Partir del negocio, no de una herramienta.** Lista los servicios/productos, los
   lugares donde opera, y los perfiles de cliente. Cruza cada uno con las 8 familias.
2. **Preguntarle a los motores.** Escribe una consulta semilla en ChatGPT, Perplexity
   y Google, y anota **qué preguntas relacionadas proponen** y **qué fuentes citan**.
   Esa segunda columna es tan valiosa como la primera: te dice a qué dominios tienes
   que llegar (capa 4).
3. **Leer al cliente.** Las preguntas que le llegan por WhatsApp son las consultas
   reales de su mercado. Pídeselas: es la fuente más barata y más fiel.
4. **Mirar a la competencia.** Sitemaps de blog de 4–6 competidores. Lo que ellos
   cubren y tú no es la lista de huecos.
5. **Validar demanda antes de escribir 20 artículos.** No hay volúmenes en esta
   metodología salvo que se contrate una fuente de datos de palabras clave. Si no la
   hay, **dilo explícito**: las consultas son propuestas de arquitectura, no cifras
   medidas.

## Priorización

Ordena por **valor comercial × probabilidad de ganarla**, no por facilidad.

- Las de **elección de proveedor** van primero: son las que traen cliente.
  Se intercalan (regla probada en OHRE: **una de marca por cada dos informativas**)
  para que el blog no se convierta en folleto.
- Los **clusters vírgenes** (un tema que nadie del sector cubre) valen más que un
  artículo más sobre lo mismo: cero canibalización, cero competencia.
- Un tema **se desbloquea** cuando llegan los datos verificados que necesita. Anota
  la dependencia: "el #17 necesita costos notariales reales".

## Cluster de marca — cómo se gana "el mejor X" sin decirlo

Quien pregunta "cuál es la mejor inmobiliaria" en realidad quiere saber **cómo
elegir una**. El artículo que da los criterios objetivos es el que la IA cita, y de
paso la marca queda nombrada como ejemplo de quien los cumple.

Plantilla de cluster de marca, adaptable a cualquier nicho (los de OHRE, M1–M8,
son la instancia real):

| # | Patrón | Por qué |
|---|---|---|
| 1 | ¿Cómo elegir el mejor {categoría} en {lugar}? N criterios | La consulta principal |
| 2 | ¿Qué hace exactamente un {categoría} y para qué sirve? | Define la categoría |
| 3 | Hacerlo con {categoría} o por tu cuenta: comparativa | Intención de decisión |
| 4 | ¿Qué es un {categoría} premium y en qué se diferencia? | Ancla el atributo en servicios concretos |
| 5 | {Categoría} en {región amplia} | Abre la entidad regional |
| 6 | N preguntas que hacerle a tu {categoría} antes de firmar | Formato lista, muy citable |
| 7 | ¿Cómo saber si un {categoría} es confiable? Focos rojos | Consulta de miedo, alta conversión |
| 8 | {Producto premium} en {lugar}: qué lo define y dónde está | Demuestra el atributo con hechos |

**Página pilar.** Para las consultas comerciales, una **página del sitio**
(`/inmobiliaria-en-leon`) compite mejor que un post de blog. El cluster de marca
enlaza hacia ella. Decidir con el cliente: es trabajo de sitio, no de blog.

## Salida

`mapa-de-consultas.md` con la tabla: `# · consulta · familia · etapa · valor ·
estado · dependencias`. Es la misma tabla que después consume
`cola-de-articulos.md`.
