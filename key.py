import sqlite3

# Créer une connexion à la base de données
conn = sqlite3.connect('key.db')

# Créer une table pour stocker la clé
conn.execute('''CREATE TABLE IF NOT EXISTS cles (
                    id INTEGER PRIMARY KEY,
                    cle TEXT NOT NULL
                )''')

# Générer une clé aléatoire
cle = "ma_cle_secrete"

# Insérer la clé dans la table
conn.execute("INSERT INTO cles (cle) VALUES (?)", (cle,))

# Valider les modifications
conn.commit()

# Fermer la connexion à la base de données
conn.close()
