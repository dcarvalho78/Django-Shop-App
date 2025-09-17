#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Static Assets sammeln (für WhiteNoise)
python manage.py collectstatic --no-input

# DB-Struktur anwenden
python manage.py migrate
