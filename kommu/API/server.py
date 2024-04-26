from flask import Flask, request, jsonify
from bb84 import prepare_qubits, bob_measure, checking, qber_key, calcul
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_provider import IBMProvider
from functions import serialize_quantum_circuit, deserialize_quantum_circuit
import numpy as np
import random

app = Flask(__name__)
qkd_sessions = {}

@app.route('/initiate', methods=['POST'])
def initiate():
    """Alice initie la session QKD."""
    data = request.json
    bits = data['bits']
    bases = data['bases']
    token = data['token']
    session_id = str(random.randint(1000, 9999))

    qc = serialize_quantum_circuit(prepare_qubits(bits, bases, token))  # Prepare qubits using Alice's function
    qkd_sessions[session_id] = {
        'quantum_circuit': qc,
        'alice_bits': bits,
        'alice_bases': bases,
        'bob_bases': None,
        'nbit_choice':2,
        'choice_index': None
    }
    return jsonify(session_id=session_id), 201

@app.route('/bob_measure/<session_id>', methods=['POST'])
def bob_measures(session_id):
    """Bob mesure les qubits préparés par Alice."""
    data = request.json
    bob_bases = data['bases']
    session = qkd_sessions[session_id]
    qc = deserialize_quantum_circuit(session['quantum_circuit'])
    measured_qc = bob_measure(qc, bob_bases)  # Bob measures the qubits
    print(f"Circuit quantique: {measured_qc}")

    # Simulate the execution of the quantum circuit
    measured_bits = calcul(measured_qc)

    session['bob_bases'] = bob_bases
    session['bob_bits'] = measured_bits
    return jsonify(message=f"Bob's measurement complete: {measured_bits}"), 200

@app.route('/compare_bases/<session_id>', methods=['POST'])
def compare_bases(session_id):
    """Comparer les bases pour identifier les bits correspondants."""
    
    data = request.json
    nbit_choice = data['nbit_choice']
    session = qkd_sessions.get(session_id)
    if not session:
        return jsonify(error="Session not found"), 404
    session['nbit_choice'] = nbit_choice

    alice_bases = session['alice_bases']
    bob_bases = session['bob_bases']
    bits = session['alice_bits']
    
    try:
        # Identifiez les indices où Alice et Bob ont utilisé la même base
        match_index, _, key = checking(len(bits), alice_bases, bob_bases, bits, nbit_choice)
        session['choice_index'] = match_index
    except ValueError as e:
        return jsonify(error=f"Erreur survenue: {e}")
    
    return jsonify(match_index=f"bases identiques: {match_index}", key=f"les cle filtre: {key}"), 200

@app.route('/calculate_qber/<session_id>', methods=['GET'])
def calculate_qber_route(session_id):
    """Calcul du QBER et détermination si la clé est sécurisée."""
    
    session = qkd_sessions[session_id]
    bits = session['alice_bits']
    bob_bits = session['bob_bits']
    choice_index = session['choice_index']

    try:
        _, check_bits_alice, _ = checking(len(bits), session['alice_bases'], session['bob_bases'], bits, len    (choice_index), choice_index)
        expeditor_key = check_bits_alice
        receiver_key = [bob_bits[i] for i in choice_index]
    except ValueError as e:
        return jsonify(error=f"Erreur survenue: {e}")

    valid, qber, final_key = qber_key(expeditor_key, receiver_key, choice_index, bits)
    
    if valid:
        return jsonify(final_key=f"the final key is: {final_key}", qber=f"the QBER is: {qber}"), 200
    else:
        return jsonify(error="QBER too high, key discarded."), 400

if __name__ == '__main__':
    app.run(debug=True)
