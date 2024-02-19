from qiskit import QuantumCircuit
import qiskit_aer as qe
from qiskit.compiler import transpile
import sqlite3

def bb84_protocol():
    # Étape 1: Créer un circuit quantique
    circuit = QuantumCircuit(2, 2)

    # Étape 2: Utiliser le protocole BB84 pour distribuer les clés quantiques
    circuit.h(0)
    circuit.cx(0, 1)

    # Étape 3: Mesurer les qubits
    circuit.measure([0, 1], [0, 1])

    # Étape 4: Exécuter le circuit sur le simulateur quantique
    simulator = qe.Aer.get_backend('qasm_simulator')
    job = simulator.run(transpile(circuit, simulator), shots=1)
    result = job.result()
    counts = result.get_counts(circuit)

    # Étape 5: Post-processing, création de la clé secrète
    key = list(counts.keys())[0]

    # Étape 6: Stockage et gestion de clés (simplifié ici)
    key_storage_system(key)

def key_storage_system(key):
    # Implémenter le stockage et la gestion de clés ici
    print("Clé secrète générée:", key)
    
    # Stocker la clé dans une base de données sécurisée, etc.
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


if __name__ == "__main__":
    # Étape préliminaire (connexion sécurisée classique)
    #secure_connection()

    # Étape principale (BB84 et gestion de clés)
    bb84_protocol()
