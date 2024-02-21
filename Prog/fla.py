from flask import Flask, render_template

from qiskit import QuantumCircuit, Aer, execute
import qiskit_aer as qe
from qiskit.compiler import transpile

app = Flask(__name__)

@app.route('/')
def home():  # sourcery skip: use-assigned-variable
    # Génération de clés quantiques entre Alice et Bob
    qc_alice = QuantumCircuit(1, 1)
    qc_alice.h(0)
    qc_alice.measure(0, 0)

    simulator = qe.Aer.get_backend('qasm_simulator')
    job_alice = simulator.run(transpile(qc_alice, simulator), shots=1)
    result_alice = job_alice.result()
    key_alice = list(result_alice.get_counts(qc_alice).keys())[0]

    # Eve intercepte la clé quantique d'Alice
    key_eve = key_alice

    # Bob reçoit la clé quantique de la part d'Alice
    key_bob = key_alice


    return render_template('index.html', key_alice=key_alice, key_eve=key_eve, key_bob=key_bob)

if __name__ == '__main__':
    app.run()
