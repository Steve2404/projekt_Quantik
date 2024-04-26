from flask import Flask, request, jsonify
from qiskit import QuantumCircuit, Aer, execute
#from qiskit.providers.ibmq import IBMQ
from qiskit.compiler import transpile, assemble
from base64 import b64encode, b64decode

app = Flask(__name__)

# Ce dictionnaire stockera les circuits quantiques
quantum_circuits = {}

def serialize_circuit(qc):
    """Sérialise un circuit quantique en une chaîne QASM encodée en base64."""
    qasm_str = qc.qasm()
    return b64encode(qasm_str.encode()).decode()

def deserialize_circuit(qasm_b64):
    """Désérialise une chaîne QASM encodée en base64 en un circuit quantique."""
    qasm_str = b64decode(qasm_b64).decode()
    return QuantumCircuit.from_qasm_str(qasm_str)

@app.route('/api/qkd/create_circuit', methods=['POST'])
def create_circuit():
    """Alice crée un circuit quantique et l'envoie."""
    data = request.json
    bits = data['bits']
    bases = data['bases']
    session_id = data['session_id']

    # Créer le circuit quantique
   # qc = prepare_qubits(bits, bases)

    # Sérialiser et stocker le circuit
    #quantum_circuits[session_id] = serialize_circuit(qc)
    return jsonify(message="Quantum circuit created and stored."), 200

@app.route('/api/qkd/retrieve_circuit', methods=['GET'])
def retrieve_circuit():
    """Bob récupère le circuit quantique."""
    session_id = request.args.get('session_id')
    qasm_b64 = quantum_circuits.get(session_id)
    if not qasm_b64:
        return jsonify(error="Circuit not found."), 404

    qc = deserialize_circuit(qasm_b64)
    backend = Aer.get_backend('aer_simulator')
    transpiled_circuit = transpile(qc, backend)
    job = execute(transpiled_circuit, backend)
    result = job.result()
    counts = result.get_counts()
    return jsonify(measurements=counts)

if __name__ == '__main__':
    app.run(debug=True)
