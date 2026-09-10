# PC Remote

Ver desde el celular si tu PC está encendida, y apagarla con un botón.

<img src="web/icono.png" width="72" align="right">

Son dos piezas:

- **El agente** (`agente.py`): un programa chiquito que corre **en la PC**. Es lo que
  contesta "estoy viva" y lo que ejecuta el apagado.
- **La interfaz web**: la sirve el propio agente. La abres en el navegador del celular
  y la agregas a la pantalla de inicio; se ve y se usa como una app.

Para instalar sin complicaciones existe `pc-remote-todo-en-uno.py`: el agente con la
web ya incrustada dentro, un archivo suelto que se descarga y se ejecuta. Se genera
con `python3 construir_archivo_unico.py` cada vez que cambia algo de `web/`.

---

## Antes de empezar: lo que esto NO puede hacer

Vale la pena ser claro para que no te lleves una sorpresa:

- **Ninguna página web puede saber sola si tu PC está prendida, ni apagarla.** Por eso
  hace falta el agente corriendo en la PC. No hay forma de evitarlo.
- **De fábrica solo funciona dentro de tu casa** (celular y PC en el mismo WiFi). Desde
  la calle no. Más abajo está cómo arreglarlo con Tailscale, en 5 minutos y gratis.
- **No puede *encender* la PC**, solo apagarla. Encenderla a distancia es otro
  mecanismo (Wake-on-LAN, se configura en la BIOS) que no está incluido aquí.
- **Si la PC está apagada, la app no se abre "sola"** con un cartelito bonito: al no
  haber servidor, el navegador muestra su error de conexión. Solo si dejas la app
  abierta y la PC se apaga, verás el estado "Apagada" en rojo.

---

## Instalación rápida (un solo archivo)

Todo esto se hace **en la PC**, no en el celular.

1. Instala Python si no lo tienes: [python.org/downloads](https://www.python.org/downloads/).
   En Windows, **marca "Add Python to PATH"** en la primera pantalla del instalador.
2. Descarga `pc-remote-todo-en-uno.py` (botón *Download raw file* en GitHub) y déjalo
   en el Escritorio. Ese archivo lleva la web incrustada: no necesita nada más al lado.
3. Doble clic. Si Windows pregunta por el firewall, dale **Permitir en redes privadas**.
4. Se abre una ventana con un enlace tipo `http://192.168.1.45:8765/?t=aB3xK9pQr2Lm`.
   Ábrelo en el celular (mismo WiFi) y agrégalo a la pantalla de inicio.

Deja esa ventana abierta: si la cierras, el agente se detiene.

El resto de este documento explica la versión en carpeta, cómo hacer que arranque
solo con la PC, y qué hacer si algo falla.

---

## Instalación completa (carpeta del repo)

### 1. Python en la PC

- **Windows**: descárgalo de [python.org/downloads](https://www.python.org/downloads/)
  y en el instalador **marca la casilla "Add Python to PATH"**.
- **macOS / Linux**: ya viene instalado.

### 2. Copia la carpeta `pc-remote` a tu PC

Donde quieras: Escritorio, Documentos, da igual.

### 3. Arranca el agente

- **Windows**: doble clic en `iniciar-agente.bat`
- **macOS / Linux**: en la terminal, `./iniciar-agente.sh`

Verás algo así:

```
  PC Remote - agente activo
  PC:      MI-PC (Windows)
  Abre esto en el celular (misma red WiFi):

     http://192.168.1.45:8765/?t=aB3xK9pQr2Lm

  Apagado con 20s de margen para cancelar.
```

Deja esa ventana abierta. Si la cierras, el agente se detiene.

### 4. Abre el enlace en el celular

Escribe esa dirección en el navegador del celular (o mándatela por WhatsApp y tócala).
Debe estar en el **mismo WiFi** que la PC.

Luego agrégala a la pantalla de inicio:

- **Android (Chrome)**: menú ⋮ → *Agregar a pantalla principal*
- **iPhone (Safari)**: botón compartir → *Añadir a pantalla de inicio*

Queda un ícono redondo como cualquier otra app.

### 5. Usarla

- El círculo verde/rojo dice si la PC está encendida.
- **Mantén pulsado** el botón rojo ~1 segundo para apagar (así no se dispara por un
  toque accidental en el bolsillo).
- Tienes **20 segundos para cancelar** antes de que se apague de verdad.

---

## Que arranque solo al prender la PC

Si no, cada vez tendrías que ir a la PC a lanzar el agente — lo cual anula bastante
la gracia del asunto.

**Windows:**

1. Pulsa `Win + R`, escribe `shell:startup` y Enter.
2. Se abre una carpeta. Arrastra ahí un **acceso directo** a `iniciar-agente.bat`
   (clic derecho sobre el .bat → *Enviar a* → *Escritorio*, y mueve ese acceso directo
   a la carpeta que se abrió).

Si te molesta la ventana negra, crea al lado del .bat un archivo `oculto.vbs` con:

```vbs
CreateObject("WScript.Shell").Run "iniciar-agente.bat", 0, False
```

y pon el acceso directo a ese `.vbs` en `shell:startup`.

**Linux (systemd):** crea `~/.config/systemd/user/pc-remote.service`:

```ini
[Unit]
Description=Agente PC Remote
[Service]
ExecStart=/usr/bin/python3 %h/pc-remote/agente.py
Restart=always
[Install]
WantedBy=default.target
```

y luego `systemctl --user enable --now pc-remote`.

**macOS:** *Ajustes del Sistema → General → Ítems de inicio de sesión* → añade
`iniciar-agente.sh`.

---

## Que la IP no cambie

La dirección `192.168.1.45` la asigna tu router y **puede cambiar** al reiniciar, y
entonces el acceso directo del celular deja de funcionar. Para fijarla, entra a la
configuración de tu router y busca *DHCP reservation* / *IP estática* / *Asignación
manual*, y ata la IP a tu PC. El nombre exacto varía según la marca del router.

Alternativa sin tocar el router: en muchas redes caseras funciona usar el nombre de la
PC en vez de la IP, por ejemplo `http://MI-PC.local:8765/?t=...`. Pruébalo; no funciona
en todas las redes.

---

## Usarla fuera de casa

La forma sensata, sin abrir puertos en el router (abrir puertos expone tu PC a
internet — no lo hagas):

1. Instala [Tailscale](https://tailscale.com/) en la PC **y** en el celular, con la
   misma cuenta. Es gratis para uso personal.
2. Tailscale le da a tu PC una IP fija tipo `100.x.y.z` que funciona desde cualquier
   lado, como si estuvieras en casa.
3. Usa esa IP en el enlace: `http://100.x.y.z:8765/?t=tu-token`.

No hay que cambiar nada del código.

*Nota: no tengo forma de verificar aquí el estado actual del plan gratuito de
Tailscale ni de sus pantallas de configuración, que cambian seguido. Verifícalo en su
web.*

---

## Seguridad

- El acceso está protegido por un **token** aleatorio que se genera solo en la primera
  ejecución y se guarda en `config.json` (ese archivo no se sube a git). Sin token, las
  peticiones se rechazan con 401.
- **El tráfico va en HTTP plano**, sin cifrar. Dentro de tu red doméstica es un riesgo
  bajo, pero es real: alguien conectado a tu WiFi y capturando tráfico podría leer el
  token y apagarte la PC. No lo uses en un WiFi público o compartido con desconocidos.
- Si crees que el token se filtró: `python3 agente.py --nuevo-token` (y vuelve a abrir
  el enlace nuevo en el celular).
- Lo peor que puede hacer alguien con el token es apagarte la PC. No da acceso a
  archivos ni a nada más: el agente solo expone estado y apagado.

---

## Ajustes

En `config.json` (se crea al primer arranque):

```json
{ "token": "...", "segundos_para_apagar": 20 }
```

Sube `segundos_para_apagar` si quieres más margen para arrepentirte.

Cambiar el puerto: `python3 agente.py --puerto 9000`.

---

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| El celular no abre la página | No están en el mismo WiFi, o el firewall de Windows bloquea el puerto. La primera vez Windows pregunta: dale **Permitir acceso en redes privadas**. |
| Funcionaba y de pronto no | Cambió la IP de la PC. Mira la que imprime el agente al arrancar. |
| Dice "token inválido" | Vuelve a abrir el enlace completo que imprime el agente (con el `?t=...`). |
| Pulso apagar y no pasa nada (Linux) | El usuario no tiene permiso para `systemctl poweroff`. En escritorios normales sí lo tiene; en un servidor sin sesión gráfica hay que configurar polkit o sudo. |
| `Address already in use` | El agente ya está corriendo. |
