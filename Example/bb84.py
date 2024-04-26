import random

def bb84_protocol():
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(10)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]

    # Encodage des qubits par Alice
    alice_qubits = []
    for i in range(10):
        if alice_bases[i] == 'rectilinear':
            if secret_key[i] == 0:
                alice_qubits.append('H')
            else:
                alice_qubits.append('V')
        elif secret_key[i] == 0:
            alice_qubits.append('D45')
        else:
            alice_qubits.append('D135')

    # Mesure des qubits par Bob
    bob_measurements = []
    for i in range(10):
        if bob_bases[i] == 'rectilinear':
            if alice_qubits[i] == 'H':
                bob_measurements.append('H')
            elif alice_qubits[i] == 'V':
                bob_measurements.append('V')
            else:
                bob_measurements.append(random.choice(['H', 'V']))
        elif alice_qubits[i] == 'D45':
            bob_measurements.append('D45')
        elif alice_qubits[i] == 'D135':
            bob_measurements.append('D135')
        else:
            bob_measurements.append(random.choice(['D45', 'D135']))

    matching_indices = [i for i in range(10) if alice_bases[i] == bob_bases[i]]
    # Extraction de la clé partagée
    shared_key = [secret_key[i] for i in matching_indices]

    # Affichage des résultats
    print("Clé secrète d'Alice :", secret_key)
    print("Bases d'Alice :", alice_bases)
    print("Bases de Bob :", bob_bases)
    print("Mesures de Bob :", bob_measurements)
    print("Clé partagée :", shared_key)

# Exemple d'utilisation du protocole BB84
bb84_protocol()
