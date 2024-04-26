import sys
from qiskit import QuantumCircuit
import base64
from qiskit_ibm_provider import IBMProvider
import socket
import threading
from bb84 import intercept_measure
from read_file import read_file


from function import *

# kommu/chat4/token.txt
# Quantum/projekt_Quantik/kommu/chat4/token.txt
token = read_file("kommu/chat4/token.txt")

HOST, PORT = "192.168.200.52", 9999
nb_bits = 20
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        send(sock, "REGISTER", 'Eve')
        base = np.random.randint(2, size=nb_bits)

        try:
            while True:
                data = sock.recv(4096)
                if not data: 
                    break    
                action, content = decode_message(data)
                if action == "QC":
                    qc_str = base64.b64decode(content).decode('utf-8')
                    qc = QuantumCircuit.from_qasm_str(qc_str) 
                    qc = intercept_measure(qc, base)
                    print(qc.draw())
                    
                    qc_str = qc.qasm()
                    qc_qasm = base64.b64encode(qc_str.encode()).decode('utf-8')
                    send(sock, "QC", qc_qasm)
                    print("Envois du QC au server !!!")
                else:
                    print(f"Received sms: {action}: {content}" )

        except Exception as e:
            print("Error receiving data:", e)



except socket.error as e:
    print(f"Failed to connect to {HOST}:{PORT}, error: {e}")
    sys.exit(1)
 

