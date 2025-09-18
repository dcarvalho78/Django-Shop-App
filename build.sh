#!/usr/bin/env bash
set -o errexit

# Installiere Abhängigkeiten
pip install -r requirements.txt

# Sammle statische Dateien für WhiteNoise
python manage.py collectstatic --no-input

# Führe Datenbankmigrationen aus
python manage.py migrate
