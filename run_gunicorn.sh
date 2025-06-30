#!/usr/bin/env bash
# Ejecuta la aplicacion Game Hub usando Gunicorn
exec gunicorn gamehub:app
