import os
from flask import Flask, jsonify, request, abort
from qiskit import QuantumCircuit, Aer, transpile, execute
import base64
import numpy as np
from bb84 import prepare_qubits, bob_measure, checking, qber_key, calcul
from functions import serialize_quantum_circuit, deserialize_quantum_circuit

app = Flask(__name__)

# gunicorn --certfile=server.crt --keyfile=server.key -b :443 app:app


# Stockage des sessions et des clés
qkd_sessions = {}

@app.route('/api/sessions', methods=['POST'])
def create_session():
    session_id = generate_session_id()
    qkd_sessions[session_id] = {'alice_circuit': None, 'bob_bases': None, 'alice_bases': None, 'indices_check_bits': None, 'final_key': None}
    return jsonify(session_id=session_id), 201


@app.route('/api/sessions/<session_id>/alice', methods=['POST'])
def alice_prepares_qubits(session_id):
    data = request.json
    bits = data['bits']
    bases = data['bases']
    circuit = prepare_qubits(bits, bases)
    serialized_circuit = serialize_quantum_circuit(circuit)
    qkd_sessions[session_id]['alice_circuit'] = serialized_circuit
    qkd_sessions[session_id]['alice_bases'] = bases
    return jsonify(message="Alice's qubits prepared."), 200

@app.route('/api/sessions/<session_id>/bob', methods=['POST'])
def bob_measures_qubits(session_id):
    data = request.json
    bases = data['bases']
    serialized_circuit = qkd_sessions[session_id]['alice_circuit']
    circuit = deserialize_quantum_circuit(serialized_circuit)
    measurements = bob_measure(circuit, bases)
    print("Measurements:", measurements)  # Ajouter un log pour voir les mesures
    qkd_sessions[session_id]['bob_bases'] = bases
    qkd_sessions[session_id]['bob_measurements'] = measurements
    return jsonify(measurements=serialize_quantum_circuit(measurements)), 200




@app.route('/api/sessions/<session_id>/exchange_bits', methods=['POST'])
def exchange_check_bits(session_id):
    if not request.is_json:
        return jsonify(error="MIME type 'application/json' expected"), 415

    data = request.get_json(silent=True)
    if not data or 'bits' not in data:
        abort(400, description="Bad request: JSON data is malformed or incomplete.")

    bits = data['bits']
    bit_choice = data.get('bit_choice', 2)  # default to 2 if not provided
    alice_bases = qkd_sessions[session_id].get('alice_bases')
    bob_bases = qkd_sessions[session_id].get('bob_bases')

    if not all([bits, alice_bases, bob_bases]):
        abort(400, description="Missing data for QKD operation.")

    try:
        choice_index, check_bits_alice, key = checking(len(bits), alice_bases, bob_bases, bits, bit_choice)
    except ValueError as e:
        return jsonify(error=str(e)), 400

    expeditor_key = [bits[i] for i in choice_index]
    receiver_key = [qkd_sessions[session_id]['bob_measurements'][i] for i in choice_index]

    valid, qber, final_key = qber_key(expeditor_key, receiver_key, choice_index, key)
    if valid:
        qkd_sessions[session_id]['final_key'] = final_key
        return jsonify(final_key=final_key, qber=qber), 200
    else:
        return jsonify(error="QBER too high, key discarded."), 400
    

def generate_session_id():
    """Génère un ID de session unique."""
    return base64.urlsafe_b64encode(os.urandom(16)).decode()

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500




# Démarrer le serveur Flask
if __name__ == '__main__':
    app.run(debug=True)
