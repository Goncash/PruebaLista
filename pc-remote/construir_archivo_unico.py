#!/usr/bin/env python3
"""
Genera 'pc-remote-todo-en-uno.py': el agente con la web incrustada dentro.

Sirve para que instalar sea descargar UN archivo y ejecutarlo, sin carpetas.
Ejecuta esto cada vez que cambies algo dentro de web/.

    python3 construir_archivo_unico.py
"""

import base64
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
SALIDA = os.path.join(BASE_DIR, "pc-remote-todo-en-uno.py")
ARCHIVOS = ["index.html", "icono.png", "icono.svg", "app.webmanifest"]

fuente = open(os.path.join(BASE_DIR, "agente.py"), encoding="utf-8").read()

lineas = ["EMBEBIDOS = {"]
for nombre in ARCHIVOS:
    with open(os.path.join(WEB_DIR, nombre), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    lineas.append('    "%s":' % nombre)
    # troceado para que el archivo resultante siga siendo legible
    for i in range(0, len(b64), 100):
        lineas.append('        "%s"' % b64[i:i + 100])
    lineas.append("        ,")
lineas.append("}")
bloque = "\n".join(lineas)

marca = "EMBEBIDOS = {}"
if marca not in fuente:
    raise SystemExit("no se encontro '%s' en agente.py" % marca)
resultado = fuente.replace(marca, bloque, 1)

# La version todo-en-uno no tiene carpeta web/ al lado: que no la busque.
resultado = resultado.replace(
    'WEB_DIR = os.path.join(BASE_DIR, "web")',
    'WEB_DIR = os.path.join(BASE_DIR, "web")  # solo existe en el repo',
    1,
)

with open(SALIDA, "w", encoding="utf-8") as f:
    f.write(resultado)

print("generado %s (%.1f KB)" % (SALIDA, os.path.getsize(SALIDA) / 1024))
