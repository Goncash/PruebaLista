#!/usr/bin/env python3
"""
Agente de PC Remote.

Corre en la PC que quieres controlar. Levanta un servidor web chiquito en la red
local: desde el celular abres la direccion que imprime al arrancar, ves si la PC
esta prendida y tienes un boton para apagarla.

No necesita instalar nada: solo Python 3.8 o superior (libreria estandar).

Uso:
    python3 agente.py                 # puerto 8765
    python3 agente.py --puerto 9000
    python3 agente.py --nuevo-token   # regenera el token de acceso
"""

import argparse
import base64
import ctypes
import hmac
import json
import os
import platform
import secrets
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")  # solo existe en el repo


def _carpeta_datos():
    """Carpeta fija para el token y la copia instalada del agente.

    Tiene que ser siempre la misma aunque se lance una copia del script desde
    otro sitio: si el token cambiara segun desde donde se arranca, el enlace
    guardado en el celular dejaria de valer.
    """
    if platform.system() == "Windows":
        raiz = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        carpeta = os.path.join(raiz, "PCRemote")
    else:
        raiz = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config")
        carpeta = os.path.join(raiz, "pc-remote")
    try:
        os.makedirs(carpeta, exist_ok=True)
    except OSError:
        return BASE_DIR
    return carpeta


DATOS_DIR = _carpeta_datos()
CONFIG_PATH = os.path.join(DATOS_DIR, "config.json")

# La version "todo en uno" lleva aqui la web incrustada en base64. En el repo
# esta vacio y los archivos se leen de la carpeta web/.
# (lo rellena construir_archivo_unico.py)
EMBEBIDOS = {
    "index.html":
        "PCFkb2N0eXBlIGh0bWw+CjxodG1sIGxhbmc9ImVzIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgbmFtZT0i"
        "dmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLCB2aWV3cG9ydC1maXQ9Y292ZXIi"
        "Pgo8bWV0YSBuYW1lPSJ0aGVtZS1jb2xvciIgY29udGVudD0iIzBlMTExNiI+Cjx0aXRsZT5NaSBQQzwvdGl0bGU+CjxsaW5rIHJl"
        "bD0ibWFuaWZlc3QiIGhyZWY9Ii9hcHAud2VibWFuaWZlc3QiPgo8bGluayByZWw9Imljb24iIGhyZWY9Ii9pY29uby5zdmciIHR5"
        "cGU9ImltYWdlL3N2Zyt4bWwiPgo8bGluayByZWw9ImFwcGxlLXRvdWNoLWljb24iIGhyZWY9Ii9pY29uby5zdmciPgo8bWV0YSBu"
        "YW1lPSJhcHBsZS1tb2JpbGUtd2ViLWFwcC1jYXBhYmxlIiBjb250ZW50PSJ5ZXMiPgo8bWV0YSBuYW1lPSJhcHBsZS1tb2JpbGUt"
        "d2ViLWFwcC1zdGF0dXMtYmFyLXN0eWxlIiBjb250ZW50PSJibGFjay10cmFuc2x1Y2VudCI+CjxzdHlsZT4KICA6cm9vdCB7CiAg"
        "ICAtLWZvbmRvOiAjMGUxMTE2OwogICAgLS10YXJqZXRhOiAjMTcxYzI0OwogICAgLS1ib3JkZTogIzI2MmQzODsKICAgIC0tdGV4"
        "dG86ICNlN2VjZjM7CiAgICAtLXRlbnVlOiAjOGI5N2E4OwogICAgLS12ZXJkZTogIzM1YzI2YTsKICAgIC0tcm9qbzogI2U0NTc0"
        "ZjsKICAgIC0tYW1iYXI6ICNlMGEzM2M7CiAgfQogICogeyBib3gtc2l6aW5nOiBib3JkZXItYm94OyAtd2Via2l0LXRhcC1oaWdo"
        "bGlnaHQtY29sb3I6IHRyYW5zcGFyZW50OyB9CiAgYm9keSB7CiAgICBtYXJnaW46IDA7CiAgICBtaW4taGVpZ2h0OiAxMDBkdmg7"
        "CiAgICBiYWNrZ3JvdW5kOiB2YXIoLS1mb25kbyk7CiAgICBjb2xvcjogdmFyKC0tdGV4dG8pOwogICAgZm9udDogMTVweC8xLjUg"
        "LWFwcGxlLXN5c3RlbSwgQmxpbmtNYWNTeXN0ZW1Gb250LCAiU2Vnb2UgVUkiLCBSb2JvdG8sIHNhbnMtc2VyaWY7CiAgICBkaXNw"
        "bGF5OiBmbGV4OwogICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjsKICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7CiAgICBqdXN0aWZ5"
        "LWNvbnRlbnQ6IGNlbnRlcjsKICAgIHBhZGRpbmc6IDI0cHggMTZweCBjYWxjKDI0cHggKyBlbnYoc2FmZS1hcmVhLWluc2V0LWJv"
        "dHRvbSkpOwogICAgdGV4dC1hbGlnbjogY2VudGVyOwogIH0KICAucHVudG8gewogICAgd2lkdGg6IDEycHg7IGhlaWdodDogMTJw"
        "eDsgYm9yZGVyLXJhZGl1czogNTAlOwogICAgYmFja2dyb3VuZDogdmFyKC0tdGVudWUpOyBkaXNwbGF5OiBpbmxpbmUtYmxvY2s7"
        "IHZlcnRpY2FsLWFsaWduOiBtaWRkbGU7CiAgICBtYXJnaW4tcmlnaHQ6IDhweDsKICB9CiAgLnB1bnRvLm9uICB7IGJhY2tncm91"
        "bmQ6IHZhcigtLXZlcmRlKTsgYm94LXNoYWRvdzogMCAwIDAgNnB4IHJnYmEoNTMsMTk0LDEwNiwuMTUpOyB9CiAgLnB1bnRvLm9m"
        "ZiB7IGJhY2tncm91bmQ6IHZhcigtLXJvam8pOyAgYm94LXNoYWRvdzogMCAwIDAgNnB4IHJnYmEoMjI4LDg3LDc5LC4xNSk7IH0K"
        "ICAucHVudG8uZXNwZXJhIHsgYW5pbWF0aW9uOiBsYXRpZG8gMS4ycyBlYXNlLWluLW91dCBpbmZpbml0ZTsgfQogIEBrZXlmcmFt"
        "ZXMgbGF0aWRvIHsgNTAlIHsgb3BhY2l0eTogLjM7IH0gfQoKICBoMSB7IGZvbnQtc2l6ZTogMjJweDsgbWFyZ2luOiAwIDAgNHB4"
        "OyBmb250LXdlaWdodDogNjAwOyBsZXR0ZXItc3BhY2luZzogLS4wMWVtOyB9CiAgLmVzdGFkbyB7IGZvbnQtc2l6ZTogMTdweDsg"
        "Zm9udC13ZWlnaHQ6IDYwMDsgbWFyZ2luOiAwIDAgNnB4OyB9CiAgLmRldGFsbGUgeyBjb2xvcjogdmFyKC0tdGVudWUpOyBmb250"
        "LXNpemU6IDEzcHg7IG1hcmdpbjogMDsgbWluLWhlaWdodDogMjBweDsgfQoKICAudGFyamV0YSB7CiAgICB3aWR0aDogMTAwJTsg"
        "bWF4LXdpZHRoOiAzNDBweDsKICAgIGJhY2tncm91bmQ6IHZhcigtLXRhcmpldGEpOwogICAgYm9yZGVyOiAxcHggc29saWQgdmFy"
        "KC0tYm9yZGUpOwogICAgYm9yZGVyLXJhZGl1czogMThweDsKICAgIHBhZGRpbmc6IDIycHggMjBweDsKICAgIG1hcmdpbi1ib3R0"
        "b206IDI4cHg7CiAgfQoKICAuYm90b24gewogICAgcG9zaXRpb246IHJlbGF0aXZlOyBvdmVyZmxvdzogaGlkZGVuOwogICAgd2lk"
        "dGg6IDE5MHB4OyBoZWlnaHQ6IDE5MHB4OyBib3JkZXItcmFkaXVzOiA1MCU7CiAgICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1i"
        "b3JkZSk7CiAgICBiYWNrZ3JvdW5kOiB2YXIoLS10YXJqZXRhKTsKICAgIGNvbG9yOiB2YXIoLS10ZXh0byk7CiAgICBkaXNwbGF5"
        "OiBmbGV4OyBmbGV4LWRpcmVjdGlvbjogY29sdW1uOyBhbGlnbi1pdGVtczogY2VudGVyOyBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRl"
        "cjsKICAgIGdhcDogMTBweDsgY3Vyc29yOiBwb2ludGVyOyB1c2VyLXNlbGVjdDogbm9uZTsKICAgIHRyYW5zaXRpb246IHRyYW5z"
        "Zm9ybSAuMTJzIGVhc2UsIG9wYWNpdHkgLjJzIGVhc2U7CiAgICB0b3VjaC1hY3Rpb246IG1hbmlwdWxhdGlvbjsKICB9CiAgLmJv"
        "dG9uOmFjdGl2ZSB7IHRyYW5zZm9ybTogc2NhbGUoLjk3KTsgfQogIC5ib3RvbltkaXNhYmxlZF0geyBvcGFjaXR5OiAuMzU7IGN1"
        "cnNvcjogZGVmYXVsdDsgfQogIC5ib3RvbiBzdmcgeyB3aWR0aDogNDZweDsgaGVpZ2h0OiA0NnB4OyBzdHJva2U6IHZhcigtLXJv"
        "am8pOyB6LWluZGV4OiAxOyB9CiAgLmJvdG9uIHNwYW4geyBmb250LXNpemU6IDEzcHg7IGNvbG9yOiB2YXIoLS10ZW51ZSk7IHot"
        "aW5kZXg6IDE7IGxldHRlci1zcGFjaW5nOiAuMDJlbTsgfQogIC8qIExhIGJhcnJhIHNlIGxsZW5hIG1pZW50cmFzIHNlIG1hbnRp"
        "ZW5lIHB1bHNhZG8gKi8KICAucmVsbGVubyB7CiAgICBwb3NpdGlvbjogYWJzb2x1dGU7IGluc2V0OiAwOwogICAgYmFja2dyb3Vu"
        "ZDogcmdiYSgyMjgsODcsNzksLjIyKTsKICAgIHRyYW5zZm9ybTogc2NhbGVZKDApOyB0cmFuc2Zvcm0tb3JpZ2luOiBib3R0b207"
        "CiAgICB0cmFuc2l0aW9uOiB0cmFuc2Zvcm0gLjA1cyBsaW5lYXI7CiAgfQoKICAuY2FuY2VsYXIgewogICAgbWFyZ2luLXRvcDog"
        "MjZweDsgcGFkZGluZzogMTRweCAzMHB4OwogICAgYmFja2dyb3VuZDogdHJhbnNwYXJlbnQ7IGNvbG9yOiB2YXIoLS10ZXh0byk7"
        "CiAgICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1ib3JkZSk7IGJvcmRlci1yYWRpdXM6IDk5OXB4OwogICAgZm9udC1zaXplOiAx"
        "NXB4OyBmb250LXdlaWdodDogNjAwOyBjdXJzb3I6IHBvaW50ZXI7CiAgfQogIC5jdWVudGEgeyBmb250LXNpemU6IDQycHg7IGZv"
        "bnQtd2VpZ2h0OiA3MDA7IGNvbG9yOiB2YXIoLS1hbWJhcik7IG1hcmdpbjogMCAwIDJweDsgfQogIC5vY3VsdG8geyBkaXNwbGF5"
        "OiBub25lICFpbXBvcnRhbnQ7IH0KICAucGllIHsgbWFyZ2luLXRvcDogMzJweDsgY29sb3I6IHZhcigtLXRlbnVlKTsgZm9udC1z"
        "aXplOiAxMnB4OyB9Cjwvc3R5bGU+CjwvaGVhZD4KPGJvZHk+Cgo8ZGl2IGNsYXNzPSJ0YXJqZXRhIj4KICA8aDEgaWQ9Im5vbWJy"
        "ZSI+TWkgUEM8L2gxPgogIDxwIGNsYXNzPSJlc3RhZG8iPjxzcGFuIGlkPSJwdW50byIgY2xhc3M9InB1bnRvIGVzcGVyYSI+PC9z"
        "cGFuPjxzcGFuIGlkPSJ0ZXh0byI+Q29uc3VsdGFuZG/igKY8L3NwYW4+PC9wPgogIDxwIGNsYXNzPSJkZXRhbGxlIiBpZD0iZGV0"
        "YWxsZSI+PC9wPgo8L2Rpdj4KCjwhLS0gVmlzdGEgbm9ybWFsOiBib3RvbiBkZSBhcGFnYWRvIC0tPgo8ZGl2IGlkPSJ2aXN0YS1h"
        "cGFnYXIiPgogIDxidXR0b24gY2xhc3M9ImJvdG9uIiBpZD0iYm90b24iIGRpc2FibGVkPgogICAgPGRpdiBjbGFzcz0icmVsbGVu"
        "byIgaWQ9InJlbGxlbm8iPjwvZGl2PgogICAgPHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZS13aWR0"
        "aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj4KICAgICAgPHBhdGggZD0iTTEyIDN2OSIvPjxwYXRoIGQ9Ik0xOC40IDYuNmE5"
        "IDkgMCAxIDEtMTIuOCAwIi8+CiAgICA8L3N2Zz4KICAgIDxzcGFuIGlkPSJldGlxdWV0YSI+bWFudMOpbiBwdWxzYWRvPC9zcGFu"
        "PgogIDwvYnV0dG9uPgo8L2Rpdj4KCjwhLS0gVmlzdGEgZGUgY3VlbnRhIHJlZ3Jlc2l2YSAtLT4KPGRpdiBpZD0idmlzdGEtY3Vl"
        "bnRhIiBjbGFzcz0ib2N1bHRvIj4KICA8cCBjbGFzcz0iY3VlbnRhIiBpZD0ic2VndW5kb3MiPuKAkzwvcD4KICA8cCBjbGFzcz0i"
        "ZGV0YWxsZSI+YXBhZ2FuZG8gbGEgUEPigKY8L3A+CiAgPGJ1dHRvbiBjbGFzcz0iY2FuY2VsYXIiIGlkPSJjYW5jZWxhciI+Q2Fu"
        "Y2VsYXI8L2J1dHRvbj4KPC9kaXY+Cgo8cCBjbGFzcz0icGllIiBpZD0icGllIj48L3A+Cgo8c2NyaXB0PgooZnVuY3Rpb24gKCkg"
        "ewogICJ1c2Ugc3RyaWN0IjsKCiAgLy8gRWwgdG9rZW4gbGxlZ2EgZW4gbGEgVVJMICg/dD0uLi4pLiBMbyBndWFyZGFtb3MgcGFy"
        "YSBxdWUgZWwgYWNjZXNvIGRpcmVjdG8KICAvLyBkZWwgY2VsdWxhciBzaWdhIGZ1bmNpb25hbmRvIGF1bnF1ZSBzZSBwaWVyZGEg"
        "bGEgcXVlcnkuCiAgdmFyIHRva2VuID0gbmV3IFVSTFNlYXJjaFBhcmFtcyhsb2NhdGlvbi5zZWFyY2gpLmdldCgidCIpOwogIHRy"
        "eSB7CiAgICBpZiAodG9rZW4pIGxvY2FsU3RvcmFnZS5zZXRJdGVtKCJwY3JlbW90ZV90b2tlbiIsIHRva2VuKTsKICAgIGVsc2Ug"
        "dG9rZW4gPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbSgicGNyZW1vdGVfdG9rZW4iKTsKICB9IGNhdGNoIChlKSB7IC8qIG1vZG8gcHJp"
        "dmFkbzogc2VndWltb3MgY29uIGVsIHRva2VuIGRlIGxhIFVSTCAqLyB9CgogIHZhciAkID0gZnVuY3Rpb24gKGlkKSB7IHJldHVy"
        "biBkb2N1bWVudC5nZXRFbGVtZW50QnlJZChpZCk7IH07CiAgdmFyIE1BTlRFTkVSX01TID0gMTIwMDsgICAvLyBjdWFudG8gaGF5"
        "IHF1ZSBtYW50ZW5lciBwdWxzYWRvCiAgdmFyIFRJTUVPVVRfTVMgPSA0MDAwOyAgICAvLyBzaSBubyByZXNwb25kZSBlbiA0cywg"
        "bGEgZGFtb3MgcG9yIGFwYWdhZGEKCiAgdmFyIGFwYWdhbmRvID0gZmFsc2U7CgogIGZ1bmN0aW9uIHBlZGlyKHJ1dGEsIG1ldG9k"
        "bykgewogICAgdmFyIGN0cmwgPSBuZXcgQWJvcnRDb250cm9sbGVyKCk7CiAgICB2YXIgdCA9IHNldFRpbWVvdXQoZnVuY3Rpb24g"
        "KCkgeyBjdHJsLmFib3J0KCk7IH0sIFRJTUVPVVRfTVMpOwogICAgcmV0dXJuIGZldGNoKHJ1dGEgKyAiP3Q9IiArIGVuY29kZVVS"
        "SUNvbXBvbmVudCh0b2tlbiB8fCAiIiksIHsKICAgICAgbWV0aG9kOiBtZXRvZG8gfHwgIkdFVCIsCiAgICAgIGNhY2hlOiAibm8t"
        "c3RvcmUiLAogICAgICBzaWduYWw6IGN0cmwuc2lnbmFsCiAgICB9KS50aGVuKGZ1bmN0aW9uIChyKSB7CiAgICAgIGNsZWFyVGlt"
        "ZW91dCh0KTsKICAgICAgaWYgKHIuc3RhdHVzID09PSA0MDEpIHRocm93IG5ldyBFcnJvcigidG9rZW4iKTsKICAgICAgaWYgKCFy"
        "Lm9rKSB0aHJvdyBuZXcgRXJyb3IoImh0dHAiKTsKICAgICAgcmV0dXJuIHIuanNvbigpOwogICAgfSwgZnVuY3Rpb24gKGUpIHsg"
        "Y2xlYXJUaW1lb3V0KHQpOyB0aHJvdyBlOyB9KTsKICB9CgogIGZ1bmN0aW9uIGZvcm1hdGVhclRpZW1wbyhzZWcpIHsKICAgIGlm"
        "IChzZWcgPT0gbnVsbCkgcmV0dXJuICIiOwogICAgdmFyIGggPSBNYXRoLmZsb29yKHNlZyAvIDM2MDApLCBtID0gTWF0aC5mbG9v"
        "cigoc2VnICUgMzYwMCkgLyA2MCk7CiAgICBpZiAoaCA+PSAyNCkgcmV0dXJuICJlbmNlbmRpZGEgaGFjZSAiICsgTWF0aC5mbG9v"
        "cihoIC8gMjQpICsgIiBkICIgKyAoaCAlIDI0KSArICIgaCI7CiAgICBpZiAoaCA+IDApIHJldHVybiAiZW5jZW5kaWRhIGhhY2Ug"
        "IiArIGggKyAiIGggIiArIG0gKyAiIG1pbiI7CiAgICByZXR1cm4gImVuY2VuZGlkYSBoYWNlICIgKyBtICsgIiBtaW4iOwogIH0K"
        "CiAgZnVuY3Rpb24gbW9zdHJhckVuY2VuZGlkYShkKSB7CiAgICAkKCJwdW50byIpLmNsYXNzTmFtZSA9ICJwdW50byBvbiI7CiAg"
        "ICAkKCJ0ZXh0byIpLnRleHRDb250ZW50ID0gIkVuY2VuZGlkYSI7CiAgICAkKCJub21icmUiKS50ZXh0Q29udGVudCA9IGQubm9t"
        "YnJlIHx8ICJNaSBQQyI7CiAgICAkKCJkZXRhbGxlIikudGV4dENvbnRlbnQgPSBmb3JtYXRlYXJUaWVtcG8oZC5lbmNlbmRpZGFf"
        "ZGVzZGUpIHx8IChkLnNpc3RlbWEgfHwgIiIpOwogICAgJCgiYm90b24iKS5kaXNhYmxlZCA9IGZhbHNlOwoKICAgIGlmIChkLmFw"
        "YWdhbmRvKSB7CiAgICAgIGFwYWdhbmRvID0gdHJ1ZTsKICAgICAgJCgidmlzdGEtYXBhZ2FyIikuY2xhc3NMaXN0LmFkZCgib2N1"
        "bHRvIik7CiAgICAgICQoInZpc3RhLWN1ZW50YSIpLmNsYXNzTGlzdC5yZW1vdmUoIm9jdWx0byIpOwogICAgICAkKCJzZWd1bmRv"
        "cyIpLnRleHRDb250ZW50ID0gZC5mYWx0YW5fc2VndW5kb3M7CiAgICB9IGVsc2UgewogICAgICBhcGFnYW5kbyA9IGZhbHNlOwog"
        "ICAgICAkKCJ2aXN0YS1jdWVudGEiKS5jbGFzc0xpc3QuYWRkKCJvY3VsdG8iKTsKICAgICAgJCgidmlzdGEtYXBhZ2FyIikuY2xh"
        "c3NMaXN0LnJlbW92ZSgib2N1bHRvIik7CiAgICAgICQoImV0aXF1ZXRhIikudGV4dENvbnRlbnQgPSAibWFudMOpbiBwdWxzYWRv"
        "IjsKICAgIH0KICB9CgogIGZ1bmN0aW9uIG1vc3RyYXJBcGFnYWRhKCkgewogICAgYXBhZ2FuZG8gPSBmYWxzZTsKICAgICQoInB1"
        "bnRvIikuY2xhc3NOYW1lID0gInB1bnRvIG9mZiI7CiAgICAkKCJ0ZXh0byIpLnRleHRDb250ZW50ID0gIkFwYWdhZGEiOwogICAg"
        "JCgiZGV0YWxsZSIpLnRleHRDb250ZW50ID0gInNpbiByZXNwdWVzdGEgZW4gbGEgcmVkIjsKICAgICQoImJvdG9uIikuZGlzYWJs"
        "ZWQgPSB0cnVlOwogICAgJCgidmlzdGEtY3VlbnRhIikuY2xhc3NMaXN0LmFkZCgib2N1bHRvIik7CiAgICAkKCJ2aXN0YS1hcGFn"
        "YXIiKS5jbGFzc0xpc3QucmVtb3ZlKCJvY3VsdG8iKTsKICB9CgogIGZ1bmN0aW9uIG1vc3RyYXJFcnJvcihtc2cpIHsKICAgICQo"
        "InB1bnRvIikuY2xhc3NOYW1lID0gInB1bnRvIjsKICAgICQoInRleHRvIikudGV4dENvbnRlbnQgPSAiU2luIGFjY2VzbyI7CiAg"
        "ICAkKCJkZXRhbGxlIikudGV4dENvbnRlbnQgPSBtc2c7CiAgICAkKCJib3RvbiIpLmRpc2FibGVkID0gdHJ1ZTsKICB9CgogIGZ1"
        "bmN0aW9uIGNvbnN1bHRhcigpIHsKICAgIGlmICghdG9rZW4pIHsgbW9zdHJhckVycm9yKCJmYWx0YSBlbCB0b2tlbjogdnVlbHZl"
        "IGEgYWJyaXIgZWwgZW5sYWNlIGRlbCBhZ2VudGUiKTsgcmV0dXJuOyB9CiAgICBwZWRpcigiL2FwaS9lc3RhZG8iKS50aGVuKG1v"
        "c3RyYXJFbmNlbmRpZGEsIGZ1bmN0aW9uIChlKSB7CiAgICAgIGlmIChlLm1lc3NhZ2UgPT09ICJ0b2tlbiIpIG1vc3RyYXJFcnJv"
        "cigidG9rZW4gaW52YWxpZG86IGFicmUgZGUgbnVldm8gZWwgZW5sYWNlIGRlbCBhZ2VudGUiKTsKICAgICAgZWxzZSBtb3N0cmFy"
        "QXBhZ2FkYSgpOwogICAgfSk7CiAgfQoKICAvLyAtLS0gbWFudGVuZXIgcHVsc2FkbyBwYXJhIGFwYWdhciAtLS0KICB2YXIgaW5p"
        "Y2lvID0gbnVsbCwgcmFmID0gbnVsbDsKCiAgZnVuY3Rpb24gcGludGFyKCkgewogICAgdmFyIGF2YW5jZSA9IE1hdGgubWluKDEs"
        "IChEYXRlLm5vdygpIC0gaW5pY2lvKSAvIE1BTlRFTkVSX01TKTsKICAgICQoInJlbGxlbm8iKS5zdHlsZS50cmFuc2Zvcm0gPSAi"
        "c2NhbGVZKCIgKyBhdmFuY2UgKyAiKSI7CiAgICBpZiAoYXZhbmNlID49IDEpIHsgc29sdGFyKHRydWUpOyByZXR1cm47IH0KICAg"
        "IHJhZiA9IHJlcXVlc3RBbmltYXRpb25GcmFtZShwaW50YXIpOwogIH0KCiAgZnVuY3Rpb24gcHVsc2FyKGV2KSB7CiAgICBpZiAo"
        "JCgiYm90b24iKS5kaXNhYmxlZCB8fCBhcGFnYW5kbyB8fCBpbmljaW8gIT09IG51bGwpIHJldHVybjsKICAgIGV2LnByZXZlbnRE"
        "ZWZhdWx0KCk7CiAgICBpbmljaW8gPSBEYXRlLm5vdygpOwogICAgJCgiZXRpcXVldGEiKS50ZXh0Q29udGVudCA9ICJzaWd1ZSBw"
        "dWxzYW5kb+KApiI7CiAgICByYWYgPSByZXF1ZXN0QW5pbWF0aW9uRnJhbWUocGludGFyKTsKICB9CgogIGZ1bmN0aW9uIHNvbHRh"
        "cihjb21wbGV0YWRvKSB7CiAgICBpZiAoaW5pY2lvID09PSBudWxsKSByZXR1cm47CiAgICBpbmljaW8gPSBudWxsOwogICAgY2Fu"
        "Y2VsQW5pbWF0aW9uRnJhbWUocmFmKTsKICAgICQoInJlbGxlbm8iKS5zdHlsZS50cmFuc2Zvcm0gPSAic2NhbGVZKDApIjsKICAg"
        "ICQoImV0aXF1ZXRhIikudGV4dENvbnRlbnQgPSAibWFudMOpbiBwdWxzYWRvIjsKICAgIGlmIChjb21wbGV0YWRvKSBhcGFnYXIo"
        "KTsKICB9CgogIGZ1bmN0aW9uIGFwYWdhcigpIHsKICAgIGlmIChuYXZpZ2F0b3IudmlicmF0ZSkgbmF2aWdhdG9yLnZpYnJhdGUo"
        "NDApOwogICAgJCgiYm90b24iKS5kaXNhYmxlZCA9IHRydWU7CiAgICBwZWRpcigiL2FwaS9hcGFnYXIiLCAiUE9TVCIpLnRoZW4o"
        "bW9zdHJhckVuY2VuZGlkYSwgZnVuY3Rpb24gKCkgeyBtb3N0cmFyQXBhZ2FkYSgpOyB9KTsKICB9CgogIHZhciBib3RvbiA9ICQo"
        "ImJvdG9uIik7CiAgYm90b24uYWRkRXZlbnRMaXN0ZW5lcigicG9pbnRlcmRvd24iLCBwdWxzYXIpOwogIGJvdG9uLmFkZEV2ZW50"
        "TGlzdGVuZXIoInBvaW50ZXJ1cCIsIGZ1bmN0aW9uICgpIHsgc29sdGFyKGZhbHNlKTsgfSk7CiAgYm90b24uYWRkRXZlbnRMaXN0"
        "ZW5lcigicG9pbnRlcmNhbmNlbCIsIGZ1bmN0aW9uICgpIHsgc29sdGFyKGZhbHNlKTsgfSk7CiAgYm90b24uYWRkRXZlbnRMaXN0"
        "ZW5lcigicG9pbnRlcmxlYXZlIiwgZnVuY3Rpb24gKCkgeyBzb2x0YXIoZmFsc2UpOyB9KTsKICBib3Rvbi5hZGRFdmVudExpc3Rl"
        "bmVyKCJjb250ZXh0bWVudSIsIGZ1bmN0aW9uIChlKSB7IGUucHJldmVudERlZmF1bHQoKTsgfSk7CgogICQoImNhbmNlbGFyIiku"
        "YWRkRXZlbnRMaXN0ZW5lcigiY2xpY2siLCBmdW5jdGlvbiAoKSB7CiAgICBwZWRpcigiL2FwaS9jYW5jZWxhciIsICJQT1NUIiku"
        "dGhlbihtb3N0cmFyRW5jZW5kaWRhLCBmdW5jdGlvbiAoKSB7IG1vc3RyYXJBcGFnYWRhKCk7IH0pOwogIH0pOwoKICAvLyBEdXJh"
        "bnRlIGxhIGN1ZW50YSByZWdyZXNpdmEgY29uc3VsdGFtb3MgY2FkYSBzZWd1bmRvOyBlbCByZXN0bywgY2FkYSAzLgogIGNvbnN1"
        "bHRhcigpOwogIHNldEludGVydmFsKGZ1bmN0aW9uICgpIHsgaWYgKGFwYWdhbmRvKSBjb25zdWx0YXIoKTsgfSwgMTAwMCk7CiAg"
        "c2V0SW50ZXJ2YWwoZnVuY3Rpb24gKCkgeyBpZiAoIWFwYWdhbmRvKSBjb25zdWx0YXIoKTsgfSwgMzAwMCk7CiAgZG9jdW1lbnQu"
        "YWRkRXZlbnRMaXN0ZW5lcigidmlzaWJpbGl0eWNoYW5nZSIsIGZ1bmN0aW9uICgpIHsKICAgIGlmICghZG9jdW1lbnQuaGlkZGVu"
        "KSBjb25zdWx0YXIoKTsKICB9KTsKCiAgJCgicGllIikudGV4dENvbnRlbnQgPSAic29sbyBmdW5jaW9uYSBlbiBsYSBtaXNtYSBy"
        "ZWQgcXVlIGxhIFBDIjsKfSkoKTsKPC9zY3JpcHQ+CjwvYm9keT4KPC9odG1sPgo="
        ,
    "icono.png":
        "iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAYAAABS3GwHAAADTUlEQVR42u3cwU0jQRBA0Y4AiQtp+Uj+EnlABhaG8Xi6/jv8M01X"
        "PXu8C6y3949vqdpyCQJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJA"
        "AkACQAJAAkACQAJAAkACYIu+Pm8P5c4AAEAAACAAABAAAAgAAAQAAAIAAAEAgAAAQAActaTTAcAFwN3lLADwLgPA3cWcCsCjFgC/"
        "WsoSgDqCZfHPWYpXA/DBG4CHF3EKAP/6BMBWSzjpawOw6fIfvQy7fN0agmX5z1mGHb5mEcGy/ACUESzLf84iXP3rVREsy+8zQBkB"
        "AP4VCADL3/6f4DKCZflv2R+Gg2AYgCsPd+ezTEYAwElD3f08AFj+cT+OAAEA+V+JBMDy538nuIxgefQBoPwotLz6A1B+F1iWH4Ay"
        "AgAAAMDyA1BFkALgL8PNvFsAAACgBGDHAU0/764IAAAAAH/exJmrf05lefW3TOV3AQAAAMDjj3NXH4OWV3+LVH4XAAAAADz+OHv1"
        "MQgAZwcAAGcHAABnB8AHYEvU+iC8vPo7f/ldAADnBwAA5wcAAOcHAADnBwAA5wfAAJwfAAMQAAYgAAwAAAAMAAAADAAAAPxAluUH"
        "wKsQAH4c2iAAAMAgAADAIAAAwIcxH4ABMAwAAPB27PEHAK9IXv0BMBQAAPC27J4B8MrkjgEwHHcMgAG5WwAMyd0CcOKQIHCvYwBA"
        "4D4BAMB9lgFA4B4B+OPgIHCHIwB4F3B/eQAQuDcAPAq5szIAA3VXAPxjqCUE7mkoAMN1P3kAhuxe8gCOGPakgbsLALKDdw9RAEcO"
        "f8cFKH/vAMQXwfID8LSFuPJSVL5PAC6wHFdakMnfGwAXX5RXLcyk7wWAIYvz7AXa+ewAxBD8d7F2OCMAIIyovANpABD4fYg8gDIC"
        "swcgCcGsAUhCMFsAsgjMFIAkBDMEIAnBzADIYTAbAHIYzACAHAZ3DYC/viYAJAAkACQAJAAkACQAJAAkACQAJAAkACQAJAAEgEsQ"
        "ABIAEgASABIAEgASABIAEgASABIAEgASABIAEgASABIAEgASABIAEgASABIAEgASABIAEgDSS/oBWA5meTdfUXwAAAAASUVORK5C"
        "YII="
        ,
    "icono.svg":
        "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxOTIgMTkyIj4KICA8cmVjdCB3aWR0"
        "aD0iMTkyIiBoZWlnaHQ9IjE5MiIgcng9IjQyIiBmaWxsPSIjMGUxMTE2Ii8+CiAgPGcgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTQ1"
        "NzRmIiBzdHJva2Utd2lkdGg9IjEyIiBzdHJva2UtbGluZWNhcD0icm91bmQiPgogICAgPHBhdGggZD0iTTk2IDQwdjUwIi8+CiAg"
        "ICA8cGF0aCBkPSJNMTI5IDYxYTQ4IDQ4IDAgMSAxLTY2IDAiLz4KICA8L2c+Cjwvc3ZnPgo="
        ,
    "app.webmanifest":
        "ewogICJuYW1lIjogIk1pIFBDIiwKICAic2hvcnRfbmFtZSI6ICJNaSBQQyIsCiAgImRlc2NyaXB0aW9uIjogIlZlciBzaSBsYSBQ"
        "QyBlc3RhIGVuY2VuZGlkYSB5IGFwYWdhcmxhIiwKICAic3RhcnRfdXJsIjogIi4vIiwKICAiZGlzcGxheSI6ICJzdGFuZGFsb25l"
        "IiwKICAib3JpZW50YXRpb24iOiAicG9ydHJhaXQiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiMwZTExMTYiLAogICJ0aGVtZV9j"
        "b2xvciI6ICIjMGUxMTE2IiwKICAiaWNvbnMiOiBbCiAgICB7ICJzcmMiOiAiL2ljb25vLnBuZyIsICJzaXplcyI6ICIxOTJ4MTky"
        "IiwgInR5cGUiOiAiaW1hZ2UvcG5nIiwgInB1cnBvc2UiOiAiYW55IiB9LAogICAgeyAic3JjIjogIi9pY29uby5zdmciLCAic2l6"
        "ZXMiOiAiYW55IiwgInR5cGUiOiAiaW1hZ2Uvc3ZnK3htbCIgfQogIF0KfQo="
        ,
}


def leer_recurso(nombre):
    """Contenido de un archivo de la web: primero del disco, si no, incrustado."""
    ruta = os.path.join(WEB_DIR, nombre)
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return f.read()
    if nombre in EMBEBIDOS:
        return base64.b64decode(EMBEBIDOS[nombre])
    return None


SISTEMA = platform.system()  # 'Windows', 'Linux', 'Darwin'
ARRANQUE = time.time()

# Estado del apagado programado. Se protege con un lock porque el servidor
# atiende varias peticiones a la vez.
_lock = threading.Lock()
_timer = None
_apagado_en = None  # timestamp en el que se ejecutara el apagado


# --------------------------------------------------------------------------
# Configuracion / token
# --------------------------------------------------------------------------

def cargar_config(nuevo_token=False):
    config = {}
    if os.path.exists(CONFIG_PATH) and not nuevo_token:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (OSError, ValueError):
            config = {}

    if not config.get("token"):
        config["token"] = secrets.token_urlsafe(12)
        config.setdefault("segundos_para_apagar", 20)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            pass  # Windows no siempre lo permite; no es critico

    config.setdefault("segundos_para_apagar", 20)
    return config


# --------------------------------------------------------------------------
# Datos de la PC
# --------------------------------------------------------------------------

def ip_local():
    """IP de la PC dentro de la red local (no abre conexion real)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def segundos_encendida():
    """Tiempo desde que arranco el sistema. None si no se puede averiguar."""
    try:
        if SISTEMA == "Linux":
            with open("/proc/uptime", "r", encoding="utf-8") as f:
                return float(f.read().split()[0])
        if SISTEMA == "Windows":
            return ctypes.windll.kernel32.GetTickCount64() / 1000.0
        if SISTEMA == "Darwin":
            salida = subprocess.check_output(
                ["sysctl", "-n", "kern.boottime"], text=True
            )
            # formato: { sec = 1712345678, usec = 0 } ...
            sec = int(salida.split("sec =")[1].split(",")[0].strip())
            return time.time() - sec
    except Exception:
        pass
    return None


def nombre_local():
    """Nombre .local de la PC, alternativa a la IP cuando el router la cambia."""
    corto = socket.gethostname().split(".")[0]
    return corto + ".local" if corto else None


# --------------------------------------------------------------------------
# Instalacion en Windows (arranque automatico + acceso directo)
# --------------------------------------------------------------------------

SCRIPT_INSTALADO = os.path.join(DATOS_DIR, "pc-remote.py")


def _carpeta_inicio():
    return os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                        "Menu Inicio", "Programas", "Inicio")


def _carpeta_inicio_real():
    """La carpeta de Inicio cambia de nombre segun el idioma de Windows."""
    candidatas = [
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                     "Start Menu", "Programs", "Startup"),
        _carpeta_inicio(),
    ]
    for c in candidatas:
        if os.path.isdir(c):
            return c
    return candidatas[0]


def _escritorio():
    for c in (os.path.join(os.path.expanduser("~"), "Desktop"),
              os.path.join(os.path.expanduser("~"), "Escritorio"),
              os.path.join(os.environ.get("USERPROFILE", ""), "OneDrive", "Desktop")):
        if os.path.isdir(c):
            return c
    return None


def _pythonw():
    """pythonw.exe ejecuta sin ventana negra; si no esta, vale python.exe."""
    exe = sys.executable or "python"
    alterno = exe.replace("python.exe", "pythonw.exe")
    return alterno if alterno != exe and os.path.exists(alterno) else exe


def instalar(puerto):
    """Deja el agente arrancando solo con Windows. Devuelve una lista de avisos."""
    avisos = []
    if SISTEMA != "Windows":
        return ["El arranque automatico automatico solo esta implementado para "
                "Windows; en Linux/macOS mira el README."]
    if not EMBEBIDOS:
        return ["Esta es la version en carpeta: para el arranque automatico usa "
                "pc-remote-todo-en-uno.py o sigue el README."]

    # 1. copia estable del agente, para que borrar la descarga no rompa nada
    try:
        origen = os.path.abspath(__file__)
        if os.path.abspath(SCRIPT_INSTALADO) != origen:
            with open(origen, "rb") as f:
                contenido = f.read()
            with open(SCRIPT_INSTALADO, "wb") as f:
                f.write(contenido)
    except OSError as e:
        return ["No se pudo copiar el agente a %s (%s)" % (DATOS_DIR, e)]

    # 2. arranque automatico. Se registra en la clave Run del usuario y no en
    #    la carpeta "Inicio": esa carpeta cambia de nombre segun el idioma de
    #    Windows y escribir en la ruta equivocada falla en silencio.
    comando = '"%s" "%s" --puerto %d' % (_pythonw(), SCRIPT_INSTALADO, puerto)
    registrado = False
    try:
        r = subprocess.run(
            ["reg", "add", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
             "/v", "PC Remote", "/t", "REG_SZ", "/d", comando, "/f"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        registrado = r.returncode == 0
    except Exception:
        registrado = False

    if not registrado:
        # de reserva: el .vbs en la carpeta de Inicio, si es que existe
        try:
            inicio = _carpeta_inicio_real()
            if os.path.isdir(inicio):
                with open(os.path.join(inicio, "PC Remote.vbs"), "w",
                          encoding="utf-8") as f:
                    f.write('CreateObject("WScript.Shell").Run "%s", 0, False\r\n'
                            % comando.replace('"', '""'))
                registrado = True
        except OSError:
            pass
    if not registrado:
        avisos.append("No se pudo activar el arranque automatico con Windows.")

    # 3. acceso directo en el escritorio que siempre muestra la IP actual
    esc = _escritorio()
    if esc:
        try:
            with open(os.path.join(esc, "Enlace para el celular.url"), "w",
                      encoding="utf-8") as f:
                f.write("[InternetShortcut]\r\nURL=http://localhost:%d/enlace\r\n" % puerto)
        except OSError as e:
            avisos.append("No se pudo crear el acceso directo del escritorio: %s" % e)

    # 4. permiso en el firewall (necesita permisos de administrador; si no,
    #    Windows preguntara la primera vez que el celular se conecte)
    try:
        r = subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             "name=PC Remote", "dir=in", "action=allow", "protocol=TCP",
             "localport=%d" % puerto, "profile=private"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            avisos.append("No se pudo abrir el puerto en el firewall sin permisos "
                          "de administrador: cuando Windows pregunte, pulsa "
                          "'Permitir acceso' en redes privadas.")
    except Exception:
        avisos.append("No se pudo configurar el firewall automaticamente.")

    return avisos


def desinstalar():
    try:
        subprocess.run(["reg", "delete",
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                        "/v", "PC Remote", "/f"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    borrados = []
    for ruta in (os.path.join(_carpeta_inicio_real(), "PC Remote.vbs"),
                 os.path.join(_escritorio() or "", "Enlace para el celular.url")):
        try:
            if ruta and os.path.exists(ruta):
                os.remove(ruta)
                borrados.append(ruta)
        except OSError:
            pass
    print("Arranque automatico y acceso directo eliminados.")
    for b in borrados:
        print("   quitado:", b)
    print("El token sigue en %s por si lo vuelves a instalar." % CONFIG_PATH)


def comando_apagado():
    if SISTEMA == "Windows":
        return ["shutdown", "/s", "/f", "/t", "0"]
    if SISTEMA == "Darwin":
        return ["osascript", "-e", 'tell application "System Events" to shut down']
    # Linux: systemctl es lo habitual en escritorios modernos
    return ["systemctl", "poweroff"]


def ejecutar_apagado():
    global _timer, _apagado_en
    with _lock:
        _timer = None
        _apagado_en = None
    cmd = comando_apagado()
    print("[agente] apagando la PC:", " ".join(cmd), flush=True)
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print("[agente] fallo el apagado (%s), intentando alternativa" % e, flush=True)
        if SISTEMA == "Linux":
            try:
                subprocess.run(["shutdown", "-h", "now"], check=True)
            except Exception as e2:
                print("[agente] tambien fallo la alternativa:", e2, flush=True)


# --------------------------------------------------------------------------
# Codigos QR
# --------------------------------------------------------------------------


# Tabla por version: (codewords de correccion por bloque, numero de bloques,
# codewords de datos totales, centros de los patrones de alineacion)
_TABLA = {
    1: (10, 1, 16, []),
    2: (16, 1, 28, [6, 18]),
    3: (26, 1, 44, [6, 22]),
    4: (18, 2, 64, [6, 26]),
    5: (24, 2, 86, [6, 30]),
    6: (16, 4, 108, [6, 34]),
}

# --- aritmetica en GF(256) para Reed-Solomon ---
_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def _mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _polinomio_generador(grado):
    g = [1]
    for i in range(grado):
        nuevo = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            nuevo[j] ^= _mul(c, 1)
            nuevo[j + 1] ^= _mul(c, _EXP[i])
        g = nuevo
    return g


def _correccion(datos, n_ec):
    gen = _polinomio_generador(n_ec)
    resto = list(datos) + [0] * n_ec
    for i in range(len(datos)):
        coef = resto[i]
        if coef:
            for j, g in enumerate(gen):
                resto[i + j] ^= _mul(g, coef)
    return resto[len(datos):]


# --- codificacion de los datos ---

def _codificar(texto):
    datos = texto.encode("utf-8")
    for version in sorted(_TABLA):
        n_ec, bloques, total_datos, _ = _TABLA[version]
        if len(datos) + 2 <= total_datos:  # 4 bits de modo + 8 de longitud
            break
    else:
        raise ValueError("texto demasiado largo para un QR version 6")

    bits = []

    def poner(valor, n):
        for i in range(n - 1, -1, -1):
            bits.append((valor >> i) & 1)

    poner(0b0100, 4)          # modo byte
    poner(len(datos), 8)      # longitud (8 bits basta hasta la version 9)
    for b in datos:
        poner(b, 8)
    poner(0, min(4, total_datos * 8 - len(bits)))   # terminador
    while len(bits) % 8:
        bits.append(0)

    codewords = [int("".join(str(b) for b in bits[i:i + 8]), 2)
                 for i in range(0, len(bits), 8)]
    relleno = [0xEC, 0x11]
    while len(codewords) < total_datos:
        codewords.append(relleno[(len(codewords) - len(bits) // 8) % 2])

    # reparto en bloques y entrelazado
    por_bloque = total_datos // bloques
    bloques_datos = [codewords[i * por_bloque:(i + 1) * por_bloque]
                     for i in range(bloques)]
    bloques_ec = [_correccion(b, n_ec) for b in bloques_datos]

    final = []
    for i in range(por_bloque):
        for b in bloques_datos:
            final.append(b[i])
    for i in range(n_ec):
        for b in bloques_ec:
            final.append(b[i])

    salida = []
    for c in final:
        for i in range(7, -1, -1):
            salida.append((c >> i) & 1)
    salida.extend([0] * (0 if version == 1 else 7))  # bits de relleno finales
    return version, salida


# --- dibujo de la matriz ---

def _patrones(version):
    n = 17 + 4 * version
    m = [[None] * n for _ in range(n)]

    def buscador(fy, fx):
        for dy in range(-1, 8):
            for dx in range(-1, 8):
                y, x = fy + dy, fx + dx
                if 0 <= y < n and 0 <= x < n:
                    borde = dy in (-1, 7) or dx in (-1, 7)
                    anillo = dy in (0, 6) or dx in (0, 6)
                    centro = 2 <= dy <= 4 and 2 <= dx <= 4
                    m[y][x] = 0 if borde else (1 if (anillo or centro) else 0)

    buscador(0, 0)
    buscador(0, n - 7)
    buscador(n - 7, 0)

    for i in range(8, n - 8):          # patrones de sincronismo
        v = 1 if i % 2 == 0 else 0
        m[6][i] = v
        m[i][6] = v

    centros = _TABLA[version][3]
    for cy in centros:
        for cx in centros:
            if (cy < 8 and cx < 8) or (cy < 8 and cx > n - 9) or (cy > n - 9 and cx < 8):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    anillo = max(abs(dy), abs(dx))
                    m[cy + dy][cx + dx] = 1 if anillo != 1 else 0

    m[n - 8][8] = 1                    # modulo siempre oscuro

    for i in range(9):                 # zonas reservadas para el formato
        if m[8][i] is None:
            m[8][i] = 2
        if m[i][8] is None:
            m[i][8] = 2
    for i in range(n - 8, n):
        if m[8][i] is None:
            m[8][i] = 2
        if m[i][8] is None:
            m[i][8] = 2
    return m


def _colocar_datos(m, bits):
    n = len(m)
    idx = 0
    arriba = True
    col = n - 1
    while col > 0:
        if col == 6:
            col -= 1
        filas = range(n - 1, -1, -1) if arriba else range(n)
        for fila in filas:
            for c in (col, col - 1):
                if m[fila][c] is None:
                    m[fila][c] = bits[idx] if idx < len(bits) else 0
                    idx += 1
        arriba = not arriba
        col -= 2


def _mascara(i, fila, col):
    if i == 0: return (fila + col) % 2 == 0
    if i == 1: return fila % 2 == 0
    if i == 2: return col % 3 == 0
    if i == 3: return (fila + col) % 3 == 0
    if i == 4: return (fila // 2 + col // 3) % 2 == 0
    if i == 5: return (fila * col) % 2 + (fila * col) % 3 == 0
    if i == 6: return ((fila * col) % 2 + (fila * col) % 3) % 2 == 0
    return ((fila + col) % 2 + (fila * col) % 3) % 2 == 0


def _penalizacion(m):
    n = len(m)
    total = 0

    # regla 1: rachas de 5 o mas del mismo color
    for linea in list(m) + [list(col) for col in zip(*m)]:
        racha = 1
        for i in range(1, n):
            if linea[i] == linea[i - 1]:
                racha += 1
            else:
                if racha >= 5:
                    total += 3 + (racha - 5)
                racha = 1
        if racha >= 5:
            total += 3 + (racha - 5)

    # regla 2: bloques de 2x2
    for y in range(n - 1):
        for x in range(n - 1):
            if m[y][x] == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                total += 3

    # regla 3: patron 1011101 con 4 claros a un lado
    patrones = ([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1])
    for linea in list(m) + [list(col) for col in zip(*m)]:
        for i in range(n - 10):
            if list(linea[i:i + 11]) in patrones:
                total += 40

    # regla 4: desviacion respecto al 50% de modulos oscuros
    oscuros = sum(sum(f) for f in m)
    porcentaje = oscuros * 100.0 / (n * n)
    total += 10 * int(abs(porcentaje - 50) / 5)
    return total


def _formato(mascara):
    # nivel M = 0b00, seguido de los 3 bits de la mascara
    datos = (0b00 << 3) | mascara
    valor = datos << 10
    for i in range(4, -1, -1):
        if valor & (1 << (i + 10)):
            valor ^= 0b10100110111 << i
    return ((datos << 10) | valor) ^ 0b101010000010010


def _con_mascara(base, bits, mascara):
    n = len(base)
    m = [fila[:] for fila in base]
    _colocar_datos(m, bits)
    for y in range(n):
        for x in range(n):
            if base[y][x] is None and _mascara(mascara, y, x):
                m[y][x] ^= 1
            if m[y][x] == 2:      # zona de formato: clara mientras se evalua
                m[y][x] = 0
    return m


def _poner_formato(m, mascara):
    n = len(m)
    fmt = _formato(mascara)
    for i in range(15):
        bit = (fmt >> i) & 1
        # franja vertical, junto al buscador superior izquierdo
        if i < 6:
            m[i][8] = bit
        elif i < 8:
            m[i + 1][8] = bit
        else:
            m[n - 15 + i][8] = bit
        # franja horizontal
        if i < 8:
            m[8][n - 1 - i] = bit
        elif i == 8:
            m[8][7] = bit
        else:
            m[8][14 - i] = bit
    m[n - 8][8] = 1               # modulo siempre oscuro


def matriz_qr(texto):
    """Devuelve el QR como lista de listas de 0/1 (1 = modulo oscuro)."""
    version, bits = _codificar(texto)
    base = _patrones(version)

    # la mascara se elige con las zonas de formato aun en claro, igual que
    # hacen las implementaciones de referencia: escribirlas antes cambia la
    # penalizacion y puede acabar eligiendo una mascara peor
    mejor = min(range(8), key=lambda k: _penalizacion(_con_mascara(base, bits, k)))
    m = _con_mascara(base, bits, mejor)
    _poner_formato(m, mejor)
    return m


def qr_svg(texto, borde=4, escala=8):
    """El QR como SVG, listo para incrustar en una pagina."""
    m = matriz_qr(texto)
    n = len(m)
    lado = (n + borde * 2) * escala
    partes = []
    for y in range(n):
        for x in range(n):
            if m[y][x]:
                partes.append('M%d %dh%dv%dh-%dz' % (
                    (x + borde) * escala, (y + borde) * escala,
                    escala, escala, escala))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'shape-rendering="crispEdges" width="%d" height="%d">'
        '<rect width="%d" height="%d" fill="#fff"/>'
        '<path d="%s" fill="#000"/></svg>'
    ) % (lado, lado, lado, lado, lado, lado, "".join(partes))


# --------------------------------------------------------------------------
# Servidor
# --------------------------------------------------------------------------

PAGINA_ENLACE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Enlace para el celular</title>
<style>
 body { margin:0; min-height:100vh; display:flex; flex-direction:column;
        align-items:center; justify-content:center; background:#f4f6f9;
        color:#1b2430; font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
        padding:32px 16px; text-align:center; }
 h1 { font-size:22px; margin:0 0 6px; }
 p  { margin:0 0 18px; color:#5a6675; max-width:460px; }
 .qr { background:#fff; padding:16px; border-radius:16px;
       box-shadow:0 2px 14px rgba(20,30,45,.12); line-height:0; }
 .qr svg { width:260px; height:260px; }
 code { display:inline-block; margin-top:18px; padding:10px 14px; background:#fff;
        border:1px solid #dde3ea; border-radius:10px; font-size:14px;
        word-break:break-all; max-width:min(460px, 90vw); }
 .nota { margin-top:22px; font-size:13px; color:#77828f; max-width:460px; }
 b { color:#1b2430; }
</style></head><body>
 <h1>Apagar {{PC}} desde el celular</h1>
 <p>Escanea el codigo con la camara del celular. Tiene que estar en el
    <b>mismo WiFi</b> que esta PC.</p>
 <div class="qr">{{QR}}</div>
 <code>{{ENLACE}}</code>
 <p class="nota">Al abrirlo, agregalo a la pantalla de inicio del celular y
    queda como una app.<br><br>
    Si algun dia deja de funcionar porque el router le cambio la IP a la PC,
    vuelve a abrir este acceso directo: el codigo se recalcula solo.
    Tambien puedes probar <b>{{ALTERNO}}</b>, que no depende de la IP
    (funciona en muchas redes, no en todas).</p>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "PCRemote"
    config = {}

    # --- utilidades ---

    def log_message(self, formato, *args):
        print("[web] %s - %s" % (self.address_string(), formato % args), flush=True)

    def responder_json(self, datos, codigo=200):
        cuerpo = json.dumps(datos).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def responder_archivo(self, nombre, tipo):
        cuerpo = leer_recurso(nombre)
        if cuerpo is None:
            self.send_error(404, "no encontrado")
            return
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def token_valido(self, query):
        """El token puede venir por cabecera o por la URL (?t=...)."""
        esperado = self.config["token"]
        recibido = self.headers.get("X-Token") or (query.get("t") or [""])[0]
        return hmac.compare_digest(str(recibido), str(esperado))

    def estado(self):
        with _lock:
            faltan = None
            if _apagado_en is not None:
                faltan = max(0, int(round(_apagado_en - time.time())))
        return {
            "ok": True,
            "nombre": socket.gethostname(),
            "sistema": "%s %s" % (SISTEMA, platform.release()),
            "encendida_desde": segundos_encendida(),
            "agente_desde": time.time() - ARRANQUE,
            "apagando": faltan is not None,
            "faltan_segundos": faltan,
        }

    # --- rutas ---

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path in ("/", "/index.html"):
            return self.responder_archivo("index.html", "text/html; charset=utf-8")
        if url.path == "/icono.svg":
            return self.responder_archivo("icono.svg", "image/svg+xml")
        if url.path == "/icono.png":
            return self.responder_archivo("icono.png", "image/png")
        if url.path == "/app.webmanifest":
            return self.responder_archivo("app.webmanifest", "application/manifest+json")

        # Pagina con el QR: solo desde la propia PC, porque muestra el token
        # en claro. Es lo que abre el acceso directo del escritorio, y como
        # calcula la IP en cada visita, sigue siendo correcta aunque el router
        # se haya reiniciado y le haya dado otra a la PC.
        if url.path == "/enlace":
            if self.client_address[0] not in ("127.0.0.1", "::1"):
                return self.send_error(403, "esta pagina solo se abre desde la PC")
            return self.responder_enlace()

        if url.path == "/api/estado":
            if not self.token_valido(query):
                return self.responder_json({"ok": False, "error": "token invalido"}, 401)
            return self.responder_json(self.estado())

        self.send_error(404, "no encontrado")

    def responder_enlace(self):
        puerto = self.server.server_address[1]
        token = self.config["token"]
        enlace = "http://%s:%d/?t=%s" % (ip_local(), puerto, token)
        alterno = "http://%s:%d/?t=%s" % (nombre_local(), puerto, token)
        html = (PAGINA_ENLACE
                .replace("{{QR}}", qr_svg(enlace, escala=6))
                .replace("{{ENLACE}}", enlace)
                .replace("{{ALTERNO}}", alterno)
                .replace("{{PC}}", socket.gethostname()))
        cuerpo = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        global _timer, _apagado_en
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path not in ("/api/apagar", "/api/cancelar"):
            return self.send_error(404, "no encontrado")

        if not self.token_valido(query):
            return self.responder_json({"ok": False, "error": "token invalido"}, 401)

        # Vaciamos el cuerpo aunque no lo usemos, para no dejar la conexion a medias.
        largo = int(self.headers.get("Content-Length") or 0)
        if largo:
            self.rfile.read(largo)

        if url.path == "/api/apagar":
            espera = int(self.config["segundos_para_apagar"])
            with _lock:
                if _timer is not None:
                    return self.responder_json(self.estado())
                _apagado_en = time.time() + espera
                _timer = threading.Timer(espera, ejecutar_apagado)
                _timer.daemon = True
                _timer.start()
            print("[agente] apagado programado en %ss" % espera, flush=True)
            return self.responder_json(self.estado())

        # /api/cancelar
        with _lock:
            if _timer is not None:
                _timer.cancel()
                _timer = None
                _apagado_en = None
                print("[agente] apagado cancelado", flush=True)
        return self.responder_json(self.estado())


def _abrir_navegador(puerto):
    try:
        import webbrowser
        webbrowser.open("http://localhost:%d/enlace" % puerto)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Agente de PC Remote")
    parser.add_argument("--puerto", type=int, default=8765)
    parser.add_argument("--nuevo-token", action="store_true",
                        help="genera un token nuevo (invalida el celular ya vinculado)")
    parser.add_argument("--no-instalar", action="store_true",
                        help="no tocar el arranque automatico de Windows")
    parser.add_argument("--desinstalar", action="store_true",
                        help="quitar el arranque automatico y el acceso directo")
    args = parser.parse_args()

    if args.desinstalar:
        desinstalar()
        return

    config = cargar_config(nuevo_token=args.nuevo_token)
    Handler.config = config

    ip = ip_local()
    enlace = "http://%s:%d/?t=%s" % (ip, args.puerto, config["token"])
    primera_vez = not os.path.exists(os.path.join(DATOS_DIR, "instalado"))

    avisos = []
    if SISTEMA == "Windows" and not args.no_instalar:
        avisos = instalar(args.puerto)
        try:
            with open(os.path.join(DATOS_DIR, "instalado"), "w") as f:
                f.write("1")
        except OSError:
            pass

    print("")
    print("  PC Remote - agente activo")
    print("  PC:      %s (%s)" % (socket.gethostname(), SISTEMA))
    if SISTEMA == "Windows" and not args.no_instalar and not avisos:
        print("  Arranca solo cada vez que enciendas Windows.")
        print("  En el escritorio tienes 'Enlace para el celular'.")
    print("  Abre esto en el celular (misma red WiFi):")
    print("")
    print("     %s" % enlace)
    print("")
    for a in avisos:
        print("  aviso: %s" % a)
    print("  Apagado con %ss de margen para cancelar." % config["segundos_para_apagar"])
    print("  Ctrl+C para detener el agente.")
    print("")

    try:
        servidor = ThreadingHTTPServer(("0.0.0.0", args.puerto), Handler)
    except OSError as e:
        print("  No se pudo abrir el puerto %d: %s" % (args.puerto, e))
        print("  Puede que el agente ya este corriendo. Prueba con otro puerto:")
        print("     python3 agente.py --puerto %d" % (args.puerto + 1))
        sys.exit(1)

    # La primera vez, abrir en la PC la pagina con el QR para no tener que
    # teclear la direccion a mano en el celular.
    if primera_vez and SISTEMA == "Windows" and not args.no_instalar:
        threading.Timer(1.0, lambda: _abrir_navegador(args.puerto)).start()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[agente] detenido")
        with _lock:
            if _timer is not None:
                _timer.cancel()
        servidor.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
