# 05 — Medición (capa 0)

**Sin esto, todo lo demás es fe.** Es también lo que convierte el servicio en un
retainer defendible: el cliente paga por una curva que sube, no por artículos.

## El problema de medir GEO

Las respuestas generativas son **no deterministas**: la misma pregunta da respuestas
distintas en corridas distintas, y están influidas por historial, ubicación y
versión del modelo. Cualquiera que te venda "posición 3 en ChatGPT" está inventando.

Lo que sí se puede medir con honestidad:

> **Frecuencia de aparición**: de N corridas de la misma consulta en sesión limpia,
> en cuántas aparece la marca.

Eso es una métrica real, comparable mes a mes, y se puede explicar sin exagerar.

## El panel de prompts

20–40 consultas fijas por cliente, sacadas del `mapa-de-consultas.md`, con
representación de las 8 familias y **sobrerrepresentación de "elección de
proveedor"** — es la que importa.

Se corren **en sesión limpia** (sin historial, sin cuenta cuando se pueda) en:

| Motor | Nota |
|---|---|
| ChatGPT (con búsqueda) | El de mayor peso por volumen de uso |
| Perplexity | El que más cita comunidad y foros |
| Google AI Overviews | Se dispara en la búsqueda normal; no en todas las consultas |
| Gemini | |
| Copilot / otros | Opcional según el mercado del cliente |

**Repetir cada consulta 3 veces** por motor. Registrar frecuencia, no un sí/no.

## Qué se registra

`panel-de-prompts.csv`, una fila por consulta × motor × medición:

```
fecha, cliente, motor, consulta, familia, apariciones_de_3, posicion_en_lista,
con_enlace, competidores_nombrados, fuentes_citadas, notas
```

**`fuentes_citadas` es la columna más valiosa del sistema.** Dice a qué dominios
está yendo el motor para responder esa pregunta en ese nicho. Esos dominios son la
lista de objetivos de la capa 4: son los sitios donde hay que estar. No es una
métrica de vanidad, es el mapa de dónde trabajar el mes siguiente.

`competidores_nombrados` da la segunda lectura: contra quién se compite realmente
en la respuesta, que casi nunca es contra quien el cliente cree.

## Cadencia

- **Línea base** antes de tocar nada. Sin línea base no hay historia que contar.
- **Mensual** a partir de ahí, el mismo día del mes.
- Cuando se publique algo relevante, **no midas al día siguiente**: los índices y
  los modelos tardan. Semanas, no horas. Decírselo al cliente por adelantado evita
  la conversación incómoda del día 3.

## Métricas complementarias (las tradicionales siguen sirviendo)

- Search Console: impresiones y clics por consulta, y páginas indexadas.
- **Tráfico de referencia desde dominios de IA** (chatgpt.com, perplexity.ai,
  gemini.google.com…) en la analítica del sitio. Suele ser pequeño en volumen y alto
  en intención.
- **Visitas de bots de IA en los logs del servidor**: dice si te están rastreando,
  que es la condición previa a que te citen. Si el hosting no da acceso a logs,
  anótalo como límite.

## Sobre `llms.txt`

Ponlo, cuesta media hora, pero **no lo vendas como la palanca**:

- Google declaró públicamente que no lo usa para sus funciones generativas, y
  ningún proveedor grande se ha comprometido a leerlo en producción para búsqueda.
- Un análisis de SE Ranking sobre adopción concluyó que su presencia **no
  correlaciona** con mayor frecuencia de citas. *Es un estudio de una empresa del
  sector, no revisado por pares — tómalo como indicio, no como prueba.*
- Donde sí tiene uso demostrado es en contextos de **agentes y documentación**
  (Anthropic lo recomienda para escribir para agentes).

Conclusión operativa: hazlo por barato y por si el estándar cuaja; la prioridad
está en las capas 1, 3 y 4.

## Herramientas

Existen plataformas comerciales de seguimiento de visibilidad en IA (Profound,
Peec, Otterly, y el módulo de los grandes suites). **No he verificado precios ni
prestaciones actuales** — si el cliente va a pagar una, compárala contra el costo de
correr el panel a mano, que para 30 consultas × 4 motores × 3 corridas es trabajo de
una tarde al mes y produce la columna de fuentes citadas, que es lo que de verdad
sirve.
