import socket
from bb84 import prepare_qubits, checking, qber
from qiskit_ibm_provider import IBMProvider
import numpy as np

def alice():
    host, port = 'localhost', 655
    
    
    nb_bits = 8
    bit_choice = 3
    alice_bits = np.random.randint(2, size=nb_bits)
    alice_basis = np.random.randint(2, size=nb_bits)
    
    choice_index_alice = [1,2,3]
    #print(f"Alice bits: {alice_bits}")
    #print(f"Alice basis: {alice_basis}")
    
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"Alice:") # Identification Alice
        response = s.recv(4096).decode()
        print(f"donnee reçu par Alice:{response}")
        
        s.sendall(f"basis:{alice_basis}".encode())
        
        # preparation of qc
        qc = prepare_qubits(alice_bits, alice_basis)
        
        # sérialiser le qc en QASM
        qc_qasm = "circuit"
        #qc_qasm = qc.qasm.dumps()
        s.sendall(f"qasm:{qc_qasm}".encode())
        
        # recevoir la base de bob
        data = s.recv(4096).decode()
        print(f"donnee reçu par Alice:{data}")
        #bob_basis = data.split(':', 1)[1]
        
        #choice_index_alice, check_bits_alice, alice_key = checking(nb_bits=nb_bits, alice_basis=alice_basis, #bob_basis=bob_basis, bits=alice_bits, bit_choice=bit_choice)
        #s.sendall(f"bit_choice:{bit_choice}".encode())
        #s.sendall(f"choice_index:{choice_index_alice}".encode())
        
if __name__ == "__main__":
    alice()
        