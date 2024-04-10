import socket
import numpy as np
import time
from functions.create_message import create_message, decode_message

def bob():  # sourcery skip: extract-method
    host, port = 'localhost', 655
    nb_bits = 8
    bob_basis = np.random.randint(2, size=nb_bits).tolist()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        # Bob envois son nom au server
        s.sendall(create_message("Bob", ""))
        
        # Bob reçois l accuse de reception du server: Bien effectue
        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "ACK":
            print("Bob connected:", content)
        
        time.sleep(5)
         
        # Bob reçois le QASM venant de d'Alice via server
        response = s.recv(4096)
        msg_type, qasm_str = decode_message(response)
        if msg_type == "QASM":
            print("Bob received(QASM):", qasm_str)
            s.sendall(create_message("ACK", "QASM received by Bob"))
        else:
            s.sendall(create_message("ACK", "(Bob-QASM) nothing received"))
            
        time.sleep(5)

        ## ************** send Basis *********************************
        # Bob reçois la base de Alice   
        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "Basis":
            print("Bob received(Alice Basis):", content)
        else:
            print("Pas reçus")
        
        while True:   
            s.sendall(create_message("Basis", str(bob_basis)))
            response = s.recv(4096)
            msg_type, content = decode_message(response)
            if msg_type == "ACK":
                print("Bob received(ACK):", content)
                break
            elif msg_type == "AW":
                print("Bob received(ACK):", content)
                time.sleep(5)
                
        ## ******************* CheckBits *******************************
        response = s.recv(4096)
        msg_type, content = decode_message(response)
        if msg_type == "CheckBits":
            print("Bob received(Alice CheckBits):", content)
            s.sendall(create_message("ACK", "CheckBits received by Bob"))
        else:
            print("Pas reçus")  
            s.sendall(create_message("ACK", "(Bob-CheckBits) nothing received"))   
                
        print("Fin de reception ...")
            
        
        
if __name__ == "__main__":
    bob()
