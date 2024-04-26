import base64
import pickle


def serialize_quantum_circuit(qc):
    qc_serialized = pickle.dumps(qc)
    qc_encoded = base64.b64encode(qc_serialized).decode('utf-8')
    return qc_encoded

def deserialize_quantum_circuit(qc_encoded):
    qc_decoded = base64.b64decode(qc_encoded.encode('utf-8'))
    qc = pickle.loads(qc_decoded)
    return qc