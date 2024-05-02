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

path_name = "Quantum/projekt_Quantik/kommu/chat4/token.txt"
#path_name = "kommu/chat4/token.txt"
token = read_file(path_name)


#HOST = "192.168.200.52"
#HOST = "192.168.0.103" 
#PORT = 9999

HOST = "localhost"
PORT = 6555

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
                # Apply the different methods based on the actions
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
                                "decis":      None,
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
                    elif action == "decis":
                        client_data[client_name]["decis"] = content
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
                        print("Change your name .....")
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
                        print("Please try again ...")
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
                            print("(ack):>You've chosen the same thing, so please try again  ....")
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
                        print("Please try again ...")
                        role = name_ask(f"{name}, do you want to be the sender or the receiver? (s/r): ".strip().lower())
                        send(sock, "CONNECT", role)
                        time.sleep(2) 
                        client_data[name]["error2"] = None

            ##******************************* Sender Seite ****************************************
            while decision_final:
                if role.startswith('s'):
                    # Initiate BB84 or any other protocol here
                    basis, bits = initiate_bb84(sock, name, n_bits, token)
                    print(f"{name} Bits's: {bits}")

                    # reception other basis
                    O_basis = deconcatenate_data(received(client_data, name, 'basis', data_lock))
                    print(f"Basis of {client_data[name]['other']}: {O_basis}")


                    print_info(name, other_name, basis, O_basis)

                    # select a number of bits for the test
                    while True:
                        bit_choice = int(input("How many bits do you want to select for the test?: "))
                        try:
                            choice_index, check_bits, key= checking(nb_bits=n_bits, alice_basis=basis, bob_basis=O_basis, bits=bits, bit_choice=bit_choice)
                            break
                        except ValueError as e:
                            print(e)
                            print("Please try again ....")

                    # send (number of bits) and (chosen index) 
                    send(sock, "INDEX", concatenate_data(choice_index))
                    send(sock, "BIT", bit_choice)
                    time.sleep(1)

                    # send check_bits
                    send(sock, "CHECK", concatenate_data(check_bits))

                    # reception of other check_bits
                    O_check_bits = deconcatenate_data(received(client_data, name, 'check_bits', data_lock))
                    print(f"Check_bits of {client_data[name]['other']}: {O_check_bits}")


                    # calculation of qber
                    response, qber, final_key = qber_key(check_bits, O_check_bits, choice_index, key)
                    send(sock, "RESP", f"{decision(response)}")

                    # reception decision
                    O_decision = received(client_data, name, 'resp', data_lock)
                    print(f"decision of {client_data[name]['other']}: {O_decision}")

            ##******************************* receiver Part ****************************************

                elif role.startswith('r'):
                    IBMProvider.save_account(token, overwrite=True)

                     # reception QC
                    qc = received(client_data, name, 'QC', data_lock)
                    qc_str = base64.b64decode(qc).decode('utf-8')
                    qc = QuantumCircuit.from_qasm_str(qc_str)


                    # Preparing to receive data
                    basis, _ = generate_bb84_data(nb_bits=n_bits)
                    send(sock, "BASIS", concatenate_data(basis))
                   
                    # qubit measurement
                    qc = bob_measure(qc, basis)
                    bits = calcul(qc)
                    print(f"{name} Bits: {bits}")
                    print(qc.draw())

                    # reception of other basis
                    O_basis = deconcatenate_data(received(client_data, name, 'basis', data_lock))
                    print(f"Basis of {client_data[name]['other']}: {O_basis}") 


                    print_info(name, other_name, basis, O_basis)

                    # reception of chosen bits
                    bit_choice = received(client_data, name, 'bit', data_lock)
                    print(f"nb of bit of {client_data[name]['other']}: {bit_choice}") 



                    # reception of chosen indexes
                    choice_index = deconcatenate_data(received(client_data, name, 'index', data_lock))
                    print(f"choice of index of {client_data[name]['other']}: {choice_index}")


                    print(f"{client_data[name]['other']} a choisir {bit_choice} bits")
                    print(f"{client_data[name]['other']} a choisir {choice_index} comme index")

                    # calculation of check_bit and choice_index
                    choice_index, check_bits, key= checking(nb_bits=n_bits, alice_basis=O_basis, bob_basis=basis, bits=bits, bit_choice=bit_choice, choice_index=choice_index)

                    # send check_bit
                    send(sock, "CHECK", concatenate_data(check_bits))


                    # reception of other check_bit
                    O_check_bits = deconcatenate_data(received(client_data, name, 'check_bits', data_lock))
                    print(f"check_bits of {client_data[name]['other']}: {O_check_bits}") 


                    # calculation of qber
                    response, qber, final_key = qber_key(O_check_bits, check_bits, choice_index, key)

                    # send decision
                    send(sock, "RESP", f"{decision(response)}")

                    # reception other  decision
                    O_decision = received(client_data, name, 'resp',data_lock )
                    print(f"decision of {client_data[name]['other']}: {O_decision}")


            ## *********************************** Conversation ******************************                        
                actions = ["basis", "bit", "QC", "index", "check_bits", "resp", "decis", "error2", "error", "ack2"]
                if response:
                    print(f"qber: {qber}")
                    print(f"final key is: {final_key}")
                    if final_key:
                        sha256_key = key_from_bits(final_key)
                        print(f"New key is: {sha256_key}")
                        
                        if compter>=3:
                            break


                        print("You must repeat this process at least 3 times to be sure of the integrity of the key. ")
                        attempt = input("Would you like to start again (y/n): ").lower()
                        decision_final = test(sock, client_data, name, data_lock, attempt)
                        compter += 1
                    
                        for action in actions:
                            client_data[name][action] = None
                        time.sleep(4)
                        
                else:
                    attempt = input("Would you like to start again (y/n): ").lower()
                    decision_final = test(sock, client_data, name, data_lock, attempt)
                    compter = 0
                    for action in actions:
                        client_data[name][action] = None
                    time.sleep(4)

            compter = 5
            if compter >3:
                while running:
                    try:
                        thread_receive = threading.Thread(target=received_msg, args=(client_data, name, 'msg',  data_lock, sha256_key), daemon=False)
                        thread_receive.start()
                        send_msg(sock, name, sha256_key)

                        thread_receive.join()

                        if client_data[name]['disc']:
                            break
                    except Exception as e:
                        print(f"Error with: {e}")
            else: 
                print("End !!!")
                    
            print("End of communication ...")
    except socket.error as e:
        print(f"Failed to connect to {HOST}:{PORT}, error: {e}")
        sys.exit(1)
 
    

if __name__ == "__main__":
    name = name_ask("Enter your name: ")
    client(name)
 