from qiskit import QuantumCircuit, Aer, execute
import random

def bb84_protocol():
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(10)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]

    # Création du circuit quantique
    qc_alice = QuantumCircuit(10, 10)
    qc_bob = QuantumCircuit(10, 10)

    # Encodage des qubits par Alice
    for i in range(10):
        if secret_key[i] != 0:
            qc_alice.x(i)
        if alice_bases[i] != 'rectilinear':
            qc_alice.h(i)

    # Mesure des qubits par Bob
    for i in range(10):
        if bob_bases[i] != 'rectilinear':
            qc_bob.h(i)

    # Simulation du circuit quantique pour Alice et Bob
    simulator = Aer.get_backend('qasm_simulator')
    job_alice = execute(qc_alice, simulator, shots=1)
    job_bob = execute(qc_bob, simulator, shots=1)

    result_alice = job_alice.result()
    result_bob = job_bob.result()

    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(10) if alice_bases[i] == bob_bases[i]]

    # Extraction de la clé partagée entre Alice et Bob
    shared_key = [secret_key[i] for i in matching_indices]

    return shared_key

# Exemple d'utilisation du protocole BB84
shared_key = bb84_protocol()
print("Clé partagée entre Alice et Bob :", shared_key)
