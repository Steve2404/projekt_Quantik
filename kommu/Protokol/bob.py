import socket
from bb84 import bob_measure
from qiskit import QuantumCircuit
import numpy as np

def bob():  # sourcery skip: extract-method
    host, port = 'localhost', 655
    nb_bits = 8
    bob_basis = np.random.randint(2, size=nb_bits)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"Bob:") # identification
        response = s.recv(4096)
        print(f"Donne recu par bob: {response}")
        s.sendall(f"basis:{bob_basis}".encode())
        
        # Attendre et recevoir qc
        received_data = s.recv(4096)
        print(f"Donne recu par bob: {received_data}")
        
        qasm_data = received_data.decode().split("qasm:", 1)[1]
        print(qasm_data)
        s.sendall("Bien reçu".encode())
        #qc = QuantumCircuit.from_qasm_str(qasm_data)
        

if __name__ == "__main__":
    bob()
        
        