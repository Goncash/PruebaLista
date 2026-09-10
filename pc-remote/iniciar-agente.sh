#!/usr/bin/env bash
# Arranca el agente de PC Remote en Linux o macOS.
cd "$(dirname "$0")"
exec python3 agente.py "$@"
