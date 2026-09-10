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
WEB_DIR = os.path.join(BASE_DIR, "web")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# La version "todo en uno" lleva aqui la web incrustada en base64. En el repo
# esta vacio y los archivos se leen de la carpeta web/.
# (lo rellena construir_archivo_unico.py)
EMBEBIDOS = {}


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
