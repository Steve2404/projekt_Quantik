import subprocess

# Lire le fichier requirements.txt
with open('requirements.txt', 'r') as file:
    packages = file.readlines()

# Ajouter chaque package avec Poetry
for package in packages:
    if package := package.strip():
        subprocess.run(f"poetry add {package}", shell=True)
