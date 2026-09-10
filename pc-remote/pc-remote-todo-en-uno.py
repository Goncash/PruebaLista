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
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

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
# Servidor
# --------------------------------------------------------------------------

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

        if url.path == "/api/estado":
            if not self.token_valido(query):
                return self.responder_json({"ok": False, "error": "token invalido"}, 401)
            return self.responder_json(self.estado())

        self.send_error(404, "no encontrado")

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


def main():
    parser = argparse.ArgumentParser(description="Agente de PC Remote")
    parser.add_argument("--puerto", type=int, default=8765)
    parser.add_argument("--nuevo-token", action="store_true",
                        help="genera un token nuevo (invalida el celular ya vinculado)")
    args = parser.parse_args()

    config = cargar_config(nuevo_token=args.nuevo_token)
    Handler.config = config

    ip = ip_local()
    enlace = "http://%s:%d/?t=%s" % (ip, args.puerto, config["token"])

    print("")
    print("  PC Remote - agente activo")
    print("  PC:      %s (%s)" % (socket.gethostname(), SISTEMA))
    print("  Abre esto en el celular (misma red WiFi):")
    print("")
    print("     %s" % enlace)
    print("")
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
