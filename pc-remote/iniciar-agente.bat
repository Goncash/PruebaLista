@echo off
REM Doble clic para arrancar el agente de PC Remote en Windows.
cd /d "%~dp0"
python agente.py %*
if errorlevel 1 (
  echo.
  echo No se pudo arrancar. Comprueba que Python este instalado: https://www.python.org/downloads/
  pause
)
