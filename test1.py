from qiskit import QuantumCircuit
from qiskit.compiler import transpile
import qiskit_aer as qe
import random


def bb84_protocol(N=10):
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(N)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(N)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(N)]

    # Création du circuit quantique
    qc_alice = QuantumCircuit(N, N)
    qc_bob = QuantumCircuit(N, N)

    # Encodage des qubits par Alice
    for i in range(N):
        if secret_key[i] != 0:
            qc_alice.x(i)
        if alice_bases[i] != 'rectilinear':
            qc_alice.h(i)
        qc_alice.measure(i, i)

    # Mesure des qubits par Bob
    for i in range(N):
        if bob_bases[i] != 'rectilinear':
            qc_bob.h(i)
        qc_bob.measure(i, i)

    # Simulation du circuit quantique pour Alice et Bob
    simulator = qe.Aer.get_backend('qasm_simulator')
    job_alice = simulator.run(transpile(qc_alice, simulator), shots=1)
    job_bob = simulator.run(transpile(qc_bob, simulator), shots=1)

    result_alice = job_alice.result()
    result_bob = job_bob.result()

    # Affichage des clés obtenues par Bob et Alice
    key_bob = [int(result_bob.get_counts(qc_bob).most_frequent()[i]) for i in range(N)]
    key_alice = [int(result_alice.get_counts(qc_alice).most_frequent()[i]) for i in range(N)]

    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(N) if alice_bases[i] == bob_bases[i]]

    # Extraction de la clé partagée entre Alice et Bob
    shared_key = [key_alice[i] for i in matching_indices]
    


    return key_bob, key_alice, shared_key

# Exemple d'utilisation du protocole BB84
key_bob, key_alice, shared_key = bb84_protocol()
print("Clé obtenue par Alice :", key_alice)

print("Clé obtenue par Bob :", key_bob)

print("Clé partagée entre Alice et Bob :", shared_key)
