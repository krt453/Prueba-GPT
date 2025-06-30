#!/usr/bin/env bash
# Script de configuracion inicial para Game Hub
# Crea el entorno virtual e instala las dependencias
set -e

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Entorno configurado. Activa el entorno con 'source .venv/bin/activate' y ejecuta 'python app.py' para iniciar el servidor."
