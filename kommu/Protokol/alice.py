import socket
from bb84 import prepare_qubits, calculate_parity
from qiskit_ibm_provider import IBMProvider
import numpy as np

def alice():
    host, port = 'localhost', 655
    
    
    nb_bits = 8
    alice_bits = np.random.randint(2, size=nb_bits)
    alice_basis = np.random.randint(2, size=nb_bits)
    print(f"Alice bits: {alice_bits}")
    print(f"Alice basis: {alice_basis}")
    
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"Alice:") # Identification Alice
        s.sendall(f"bases:{alice_basis}".encode())
        
        # preparation of qc
        qc = prepare_qubits(alice_bits, alice_basis)
        
        # sérialiser le qc en QASM
        qc_qasm = qc.qasm2.dumps()
        s.sendall(f"QASM:{qc_qasm}".encode())
        
        # recevoir la base de bob
        data = eval(s.recv(4096).decode())
        print(data)
        bob_basis = data.split(':', 1)[1]
        
if __name__ == "__main__":
    alice()
        