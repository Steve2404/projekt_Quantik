#!/bin/bash

# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter PyInstaller
pyinstaller --onefile --windowed main.py

# Désactiver l'environnement virtuel
deactivate

echo "L'exécutable a été créé dans le dossier dist/"
