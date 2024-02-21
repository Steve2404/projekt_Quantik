from flask import Flask, render_template

from qiskit import QuantumCircuit
import qiskit_aer as qe
from qiskit.compiler import transpile
import random

app = Flask(__name__)

def bb84_protocol():  # sourcery skip: inline-immediately-returned-variable
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(10)]

    # Génération des bases aléatoires pour Alice, Bob et Eve
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    eve_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]

    # Création du circuit quantique
    qc_alice = QuantumCircuit(10, 10)
    qc_bob = QuantumCircuit(10, 10)
    qc_eve = QuantumCircuit(10, 10)

    # Encodage des qubits par Alice
    for i in range(10):
        if secret_key[i] != 0:
            qc_alice.x(i)
        if alice_bases[i] != 'rectilinear':
            qc_alice.t(i)
        qc_alice.h(i)

    # Interception et ré-encodage des qubits par Eve
    for i in range(10):
        if alice_bases[i] != eve_bases[i]:
            qc_eve.measure(i, i)
            if eve_bases[i] != 'rectilinear':
                qc_eve.t(i)
            qc_eve.h(i)

    # Mesure des qubits par Bob
    for i in range(10):
        if bob_bases[i] != 'rectilinear':
            qc_bob.tdg(i)
        qc_bob.measure(i, i)

    # Simulation du circuit quantique pour Alice, Bob et Eve
    simulator = qe.Aer.get_backend('qasm_simulator')
    job_alice = simulator.run(transpile(qc_alice, simulator), shots=1)
    job_eve = simulator.run(transpile(qc_eve, simulator), shots=1)
    job_bob = simulator.run(transpile(qc_bob, simulator), shots=1)

    result_alice = job_alice.result()
    result_eve = job_eve.result()
    result_bob = job_bob.result()

    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(10) if alice_bases[i] == bob_bases[i]]
    response = [1 for i in range(len(alice_bases)) if alice_bases[i] != bob_bases[i]]

    # Extraction de la clé partagée entre Alice et Bob
    shared_key = [secret_key[i] for i in matching_indices]

    return shared_key, response

@app.route('/')
def home():
    shared_key, response = bb84_protocol()
    print(response)
    if len(response) > 0:
        result = "you are a spy"
    return render_template('index3.html', shared_key=shared_key, result=result)

if __name__ == '__main__':
    app.run()
