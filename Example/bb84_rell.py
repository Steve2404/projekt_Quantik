from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit_ibm_provider import IBMProvider
import qiskit_aer as qe
import random

def bb84_protocol():  
    IBMProvider.save_account('356c98ef861f7b5562320e3782b24ac7f0a7f2990b93038fb7e19a1a0ec422e0785152bb4ad77b0fdc6b7df3b977ff03ce6ec663b41e9b37429f064eb9d185bf', overwrite=True)

    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(100)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(100)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(100)]

    # Création du circuit quantique
    circuit = QuantumCircuit(100, 100)

    # Encodage des qubits par Alice
    for i in range(100):
        if secret_key[i] != 0:
            circuit.x(i)
        if alice_bases[i] != 'rectilinear':
            circuit.t(i)
        circuit.h(i)
    # Mesure des qubits par Bob
    for i in range(100):
        if bob_bases[i] != 'rectilinear':
            circuit.tdg(i)
        circuit.measure(i, i)
    # Affichage du circuit
    print(circuit.draw(output='text'))

    # Simulation du circuit quantique
    provider = IBMProvider()
    #print(provider.backends())
    simulator = provider.get_backend('simulator_mps')
    job = simulator.run(transpile(circuit, simulator), shots=1)
    job_id = job.job_id()
    
    # attendre que le travail soit termine
    retrieved_job = provider.retrieve_job(job_id)
    result = retrieved_job.result()
    counts = result.get_counts(circuit)
    keys = list(counts.keys())[0]


    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(100) if alice_bases[i] == bob_bases[i]]

    # Extraction de la clé partagée
    shared_key = [secret_key[i] for i in matching_indices]


    # Affichage des résultats
    print("Clé secrète d'Alice :", secret_key)
    print("Bases d'Alice :", alice_bases)
    print("Bases de Bob :", bob_bases)
    print("Clé partagée :", shared_key)

# Exemple d'utilisation du protocole BB84
bb84_protocol()
