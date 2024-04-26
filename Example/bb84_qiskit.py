from qiskit import QuantumCircuit
from qiskit.compiler import transpile
import qiskit_aer as qe
import random

def bb84_protocol():  
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(10)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]

    # Création du circuit quantique
    circuit = QuantumCircuit(10, 10)

    # Encodage des qubits par Alice
    for i in range(10):
        if secret_key[i] != 0:
            circuit.x(i)
        if alice_bases[i] != 'rectilinear':
            circuit.t(i)
        circuit.h(i)
    # Mesure des qubits par Bob
    for i in range(10):
        if bob_bases[i] != 'rectilinear':
            circuit.tdg(i)
        circuit.measure(i, i)
    # Affichage du circuit
    print(circuit.draw(output='text'))

    # Simulation du circuit quantique
    simulator = qe.Aer.get_backend('qasm_simulator')
    job = simulator.run(transpile(circuit, simulator), shots=1)
    result = job.result()
    #counts = result.get_counts(circuit)

    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(10) if alice_bases[i] == bob_bases[i]]

    # Extraction de la clé partagée
    shared_key = [secret_key[i] for i in matching_indices]


    # Affichage des résultats
    print("Clé secrète d'Alice :", secret_key)
    print("Bases d'Alice :", alice_bases)
    print("Bases de Bob :", bob_bases)
    print("Clé partagée :", shared_key)

# Exemple d'utilisation du protocole BB84
bb84_protocol()
