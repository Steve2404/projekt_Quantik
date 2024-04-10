import socket
import numpy as np
import time
from functions.create_message import create_message,  decode_message

def alice():  # sourcery skip: extract-method
    host, port = 'localhost', 655

    nb_bits     = 8
    alice_bits  = np.random.randint(2, size=nb_bits).tolist()
    alice_basis = np.random.randint(2, size=nb_bits).tolist()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        s.sendall(create_message("Alice", ""))

        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "ACK":
            print("Alice connected:", content)

        ## *********************** send QASM ****************************
        # Prepare et envoi d'un QASM ou autre information nécessaire
        qasm_str = "OPENQASM 2.0"
        
        while True:
            s.sendall(create_message("QASM", qasm_str))
            response = s.recv(4096)
            msg_type, content = decode_message(response)
            if msg_type == "ACK":
                print(f"Alice received(ACK): {content}")
                break
            elif msg_type == "AW":
                print(f"Alice received(ACK): {content}")                
                time.sleep(5)

        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "ACK":
            print("Alice received(ACK):", content)
        
        print("\n")
        ## ************************** Send Basis ************************    

        while True:
            # Alice envois ca base au serveur
            s.sendall(create_message("Basis", str(alice_basis)))
            # Alice reception accuse de reception du server: Bonne reception
            response = s.recv(4096)
            msg_type, content = decode_message(response)
            if msg_type == "ACK":
                print("Alice received(ACK):", content)
                break
            elif msg_type == "AW":
                print("Alice received(ACK):", content)
                time.sleep(5)  
        
        # Alice reçois la base de Bob   
        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "Basis":
            print("Alice received(Bob Basis):", content)
    
        ## ********************* send CheckBits *****************************
        while True:
            # Alice envois ca base au serveur
            s.sendall(create_message("CheckBits", str(alice_basis)))
            # Alice reception accuse de reception du server: Bonne reception
            response = s.recv(4096)
            msg_type, content = decode_message(response)
            if msg_type == "ACK":
                print("Alice received(ACK):", content)
                break
            elif msg_type == "AW":
                print("Alice received(ACK):", content)
                time.sleep(5)
                  
        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "ACK":
            print("Alice received(ACK):", content)
        

if __name__ == "__main__":
    alice()