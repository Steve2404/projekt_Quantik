from flask import Flask, render_template

from qiskit import QuantumCircuit
from qiskit.compiler import transpile
import qiskit_aer as qe
import random

app = Flask(__name__)

def bb84_protocol():
    # Génération de la clé secrète d'Alice
    secret_key = [random.randint(0, 1) for _ in range(10)]

    # Génération des bases aléatoires pour Alice et Bob
    alice_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]
    bob_bases = [random.choice(['rectilinear', 'diagonal']) for _ in range(10)]

    # Création du circuit quantique
    qc = QuantumCircuit(10, 10)

    # Encodage des qubits par Alice
    for i in range(10):
        if secret_key[i] != 0:
            qc.x(i)
        if alice_bases[i] != 'rectilinear':
            qc.t(i)
        qc.h(i)

    # Mesure des qubits par Bob
    for i in range(10):
        if bob_bases[i] != 'rectilinear':
            qc.tdg(i)
        qc.measure(i, i)

    # Simulation du circuit quantique
    simulator = qe.Aer.get_backend('qasm_simulator')
    job = simulator.run(transpile(qc, simulator), shots=1)
    result = job.result()
    counts = result.get_counts(qc)

    # Comparaison des bases utilisées par Alice et Bob
    matching_indices = [i for i in range(10) if alice_bases[i] == bob_bases[i]]

    return [secret_key[i] for i in matching_indices]

@app.route('/')
def home():
    shared_key = bb84_protocol()
    return render_template('index2.html', shared_key=shared_key)

if __name__ == '__main__':
    app.run()
