import socket
from bb84 import bob_measure
from qiskit import QuantumCircuit
import numpy as np

def bob():
    host, port = 'localhost', 505040
    nb_bits = 8
    bob_basis = np.random.randint(2, size=nb_bits)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"Bob") # identification
        s.sendall(f"bases:{bob_basis}".encode())
        
        # Attendre et recevoir qc
        received_data = s.recv(4096)
        qasm_data = received_data.decode().split("QASM:", 1)[1]
        qc = QuantumCircuit.from_qasm_str(qasm_data)
        

if __name__ == "__main__":
    bob()
        
        