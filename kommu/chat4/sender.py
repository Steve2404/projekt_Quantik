import socket
import threading
import sys
import time
from qiskit import QuantumCircuit
import base64
from qiskit_ibm_provider import IBMProvider

from function import * 
from bb84 import checking, qber_key, bob_measure, calcul
from read_file import read_file


token = read_file("Quantum/projekt_Quantik/kommu/chat4/token.txt")


HOST, PORT = "localhost", 655
n_bits = 20
running= True

client_data = {}
data_lock = threading.Lock()

def receive(sock):
    global client_data
    client_name = None  # Nom du client pour ce thread

    while True:
        try:
            if data := sock.recv(4096).decode():
                action, content = decode_message(data.encode())
                # appliquer les différentes méthodes en fonction des actions
                with data_lock:  
                    if action == "REGISTER":
                        client_name = content.split(":>")[0]
                        if client_name not in client_data:
                            client_data[client_name] = {
                                "basis":      None,
                                "bit":        None,
                                "QC":         None,
                                "index":      None,
                                "check_bits": None,
                                "resp":       None,
                                "msg":        None,
                                "other":      None,
                                "error2":     None,
                                "error":      None,
                                "ack":        content,
                                "ack2":       None,
                                "role":       None,
                                "disc":       None
                            }

                    elif action == "MESSAGE":
                        message = content.split(":>")[1]
                        if client_name:
                            client_data[client_name]["msg"] = message
                    elif action == "OTHER":
                        client_data[client_name]["other"] = content
                    elif action == "ERROR2":
                        client_data[client_name]["error2"] = content
                    elif action == "ERROR":
                        client_name, content = content.split(":>")
                        client_data[client_name]["error"] = content
                    elif action == "ACK":
                        client_data[client_name]["ack"] = content
                    elif action == "ACK2": 
                        client_data[client_name]["ack2"] = content
                    elif action == "ROLE":
                        client_data[client_name]["role"] = content
                    elif action == "QC":
                        client_data[client_name]["QC"] = content 
                    elif action == "basis":
                        client_data[client_name]["basis"] = content
                    elif action == "index":
                        client_data[client_name]["index"] = content
                    elif action == "check_bits":
                        client_data[client_name]["check_bits"] = content
                    elif action == "resp":
                        client_data[client_name]["resp"] = content
                    elif action == "bit":
                        client_data[client_name]["bit"] = content
                    elif action == "disc":
                        client_data[client_name]["disc"] = content
                    else: 
                        print("No action detect !!!!")
                    
            else:
                print("No data received, server may have closed the connection.")
                break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def client(name): 
    global running  
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            threading.Thread(target=receive, args=(sock,), daemon=True).start()

            send(sock, "REGISTER", name)

            while True:
                time.sleep(2)  
                with data_lock:
                    if client_data[name]['ack'] is not None:
                        print(f"(ack):> {client_data[name]['ack']}")
                        break
                    elif client_data[name]['error'] is not None:
                        print(f"(error):> {client_data[name]['error']}")
                        print("Changez de nom .....")
                        name = name_ask("Enter your name: ")
                        send(sock, "REGISTER", name)


            other_name = input("Enter the name of the client you wish to connect to: ")
            send(sock, "CONNECT", other_name)
            while True:
                time.sleep(2)  
                with data_lock:
                    if client_data[name]['ack'] is not None and client_data[name]['error2'] is  None:
                        print(f"(ack):> {client_data[name]['ack']}")
                        break
                    elif client_data[name]['ack2'] is not None: 
                        print(f"(ack):> {client_data[name]['ack']}")
                        break
                    else:
                        print(f"(error):> {client_data[name]['error2']}")
                        print("Veillez réessayer ...")
                        other_name = name_ask("Enter the name of the client you wish to connect to: ")
                        send(sock, "CONNECT", other_name)
                        time.sleep(2)
                        client_data[name]['error2'] = None
                    
            role = input(f"{name}, do you want to be the sender or the receiver? (s/r): ").strip().lower()
            send(sock, "ROLE", role)

            decision_final = True
            compter = 0


            while True:
                time.sleep(2)
                with data_lock:
                    if client_data[name]["role"] is not None:
                        other_role = client_data[name]["role"]
                        if other_role == role:
                            print("(ack):> Vous avez choisi la meme chose, veillez réessayer ....")
                            role = name_ask(f"{name}, do you want to be the sender or the receiver? (s/r): ".strip().lower())
                            send(sock, "ROLE", role)
                            time.sleep(2)
                            client_data[name]["role"] = None
                        else:
                            response = "(ack):> You are the sender." if role.startswith('s') else "(ack):> You are the receiver"
                            print(response)
                            break
                    elif client_data[name]["error2"] is not None:
                        print(f"(error):> {client_data[name]['error2']}")
                        print("Veillez réessayer ...")
                        role = name_ask(f"{name}, do you want to be the sender or the receiver? (s/r): ".strip().lower())
                        send(sock, "CONNECT", role)
                        time.sleep(2) 
                        client_data[name]["error2"] = None

            ##******************************* Sender Seite ****************************************
            while decision_final and compter <3:
                if role.startswith('s'):
                    # Initiate BB84 or any other protocol here
                    basis, bits = initiate_bb84(sock, name, n_bits, token)
                    print(f"{name}'s Bits: {bits}")

                    # reception other basis
                    O_basis = deconcatenate_data(received(client_data, name, 'basis', data_lock))
                    print(f"Basis of {client_data[name]['other']}: {O_basis}")


                    print_info(name, other_name, basis, O_basis)

                    # selection un nbre de bit pour le test
                    while True:
                        bit_choice = int(input("Combien de bit voulez vous sélectionner pour faire le teste: "))
                        try:
                            choice_index, check_bits, key= checking(nb_bits=n_bits, alice_basis=basis, bob_basis=O_basis, bits=bits, bit_choice=bit_choice)
                            break
                        except ValueError as e:
                            print(e)
                            print("Veillez réessayer ....")

                    # envois du (nbre de bit) et (index choisi) 
                    send(sock, "INDEX", concatenate_data(choice_index))
                    send(sock, "BIT", bit_choice)
                    time.sleep(1)

                    # envois check_bits
                    send(sock, "CHECK", concatenate_data(check_bits))

                    # reception other check_bits
                    O_check_bits = deconcatenate_data(received(client_data, name, 'check_bits', data_lock))
                    print(f"Check_bits of {client_data[name]['other']}: {O_check_bits}")


                    # calcul du qber
                    response, qber, final_key = qber_key(check_bits, O_check_bits, choice_index, key)
                    send(sock, "RESP", f"{decision(response)}")

                    # reception decision
                    O_decision = received(client_data, name, 'resp', data_lock)
                    print(f"decision of {client_data[name]['other']}: {O_decision}")
                            
            ##******************************* receiver Seite ****************************************

                elif role.startswith('r'):
                    IBMProvider.save_account(token, overwrite=True)

                    # Prepare to receive data
                    basis, _ = generate_bb84_data(nb_bits=n_bits)
                    send(sock, "BASIS", concatenate_data(basis))

                    # reception QC
                    qc = received(client_data, name, 'QC', data_lock)
                    qc_str = base64.b64decode(qc).decode('utf-8')
                    qc = QuantumCircuit.from_qasm_str(qc_str)

                    # mesure des qubits
                    qc = bob_measure(qc, basis)
                    bits = calcul(qc)
                    print(f"{name} Bits: {bits}")
                    print(qc.draw())

                    # reception other basis
                    O_basis = deconcatenate_data(received(client_data, name, 'basis', data_lock))
                    print(f"Basis of {client_data[name]['other']}: {O_basis}") 


                    print_info(name, other_name, basis, O_basis)

                    # reception bit choice
                    bit_choice = received(client_data, name, 'bit', data_lock)
                    print(f"nb of bit of {client_data[name]['other']}: {bit_choice}") 



                    # reception choix index
                    choice_index = deconcatenate_data(received(client_data, name, 'index', data_lock))
                    print(f"choice of index of {client_data[name]['other']}: {choice_index}")


                    print(f"{client_data[name]['other']} a choisir {bit_choice} bits")
                    print(f"{client_data[name]['other']} a choisir {choice_index} comme index")

                    # calcul check_bit et choice_index
                    choice_index, check_bits, key= checking(nb_bits=n_bits, alice_basis=O_basis, bob_basis=basis, bits=bits, bit_choice=bit_choice, choice_index=choice_index)

                    # envois check_bit
                    send(sock, "CHECK", concatenate_data(check_bits))


                    # reception other check_bit
                    O_check_bits = deconcatenate_data(received(client_data, name, 'check_bits', data_lock))
                    print(f"check_bits of {client_data[name]['other']}: {O_check_bits}") 


                    # calcul qber
                    response, qber, final_key = qber_key(O_check_bits, check_bits, choice_index, key)

                    # envois decision
                    send(sock, "RESP", f"{decision(response)}")

                    # reception other  decision
                    O_decision = received(client_data, name, 'resp',data_lock )
                    print(f"decision of {client_data[name]['other']}: {O_decision}")
                    
            
            ## *********************************** Conversation ******************************                        

                if response:
                    print(f"qber: {qber}")
                    print(f"final key is: {final_key}")
                    if final_key:
                        sha256_key = generate_sha256_key(final_key)
                        print(f"Nouvelle cle est: {sha256_key}")
                        
                    print("Vous devez refaire se processus au moins 3 fois pour être sure de l intégrité de la cle ")
                    attempt = input("Voulez vous recommencer (y/n): ").lower()
                    decision_final = test(sock, client_data, name, data_lock, attempt)
                    #compter += 1
                    compter = 5
            
                else:
                     attempt = input("Voulez vous recommencer (y/n): ").lower()
                     decision_final = test(sock, client_data, name, data_lock, attempt)
                     compter = 0
                     
                   
            while running:
                thread_receive = threading.Thread(target=received_msg, args=(client_data, name, 'msg', data_lock), daemon=True)
                thread_receive.start()
                send_msg(sock, name)
                
                thread_receive.join()
                
                if client_data[name]['disc']:
                    print("Sortie de la boucle infini")
                    break
                      
            print("Fin de la communication ...")
    except socket.error as e:
        print(f"Failed to connect to {HOST}:{PORT}, error: {e}")
        sys.exit(1)
 
    

if __name__ == "__main__":
    name = name_ask("Enter your name: ")
    client(name)
