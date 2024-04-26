import socket
import threading
from function import *


clients = {}



token = read_file2("Quantum/projekt_Quantik/kommu/chat4/token.txt")


def client(sock, addr):  
    global clients
    client_name = None

    while True:
        try:
            data = sock.recv(4096)
            print(clients)
            if not data:
                break

            msg_type, content = decode_message(data)
            if msg_type == "REGISTER":
                client_name = content
                if client_name in clients:
                    send(sock, "ERROR", f"{client_name}:>Name already in use.")
                    
                #elif client_name == "Eve":
                #    print(f"Eve vient de se connecter: {client_name}")
                #    clients[client_name] ={'conn': sock, 'other': None, 'spion':'spion'}
                else:
                    clients[client_name] = {'conn': sock, 'other': None}
                    print(f"{client_name} registered from {addr}")
                    send(sock, "REGISTER", f"{client_name}:>Registered successfully.")


            elif msg_type == "CONNECT":
                target_name = content.strip()
                # Assurer que le client cible existe
                if target_name not in clients:
                    send(sock, "ERROR2", f"{target_name} not available.")
                else:
                    target_client = clients[target_name]
                    current_client = clients[client_name]

                    # Vérifie si le client cible est le même que le client actuel
                    if target_client['conn'] == current_client['conn']:
                        send(sock, "ERROR2", "You cannot communicate with yourself.")
                        # Vérifie si le client actuel ou le client cible est déjà connecté à quelqu'un d'autre
                    elif current_client['other'] is not None or target_client['other'] is not None:
                        if current_client['other'] == target_client['conn']:
                            # Si déjà connectés l'un à l'autre
                            send(sock, "ACK2", f"{target_name} Is already connected to you.")
                            send(sock, "ACK", f"Connected to {target_name}.")
                            send(target_client['conn'], "OTHER", client_name)
                        else:
                            # Si déjà connectés mais pas l'un à l'autre
                            send(sock, "ERROR2", f"{target_name} is already connected to someone else.")
                    else:
                        # Connecter les deux clients
                        current_client['other'] = target_client['conn']
                        target_client['other'] = sock
                        print(f"je suis entrain de joindre les deux: {clients.get('Eve')}")
                        
                        #if clients["Eve"]:
                        #    clients["Eve"]["other"] = target_client['conn']

                        # Envoyer les confirmations de connexion
                        send(sock, "ACK", f"Connected to {target_name}.")
                        send(target_client['conn'], "OTHER", client_name)

            # interception du QC par Eve  
            #elif clients['Eve']['spion'] and msg_type == 'QC':
            #    if msg_type == "QC":
            #        eve_sock = clients['Eve']['conn']
            #        send(eve_sock, 'QC', content)
            #        clients['Eve']['spion'] = None
                   

            elif msg_type in ["MESSAGE", "ROLE", "QC", "BASIS", "INDEX", "CHECK", "RESP", "BIT"]:

                if other_sock := clients[client_name]['other']:
                    # Mapping des types de messages à leurs noms de commande correspondants sur le réseau
                    message_types = {
                                        "MESSAGE": "MESSAGE",
                                        "ROLE": "ROLE",
                                        "QC": "QC",
                                        "BASIS": "basis",
                                        "INDEX": "index",
                                        "CHECK": "check_bits",
                                        "RESP": "resp",
                                        "BIT": "bit"
                                    }
                    if command := message_types.get(msg_type):
                        full_message = f"{client_name}:>{content}" if msg_type == "MESSAGE" else content
                        send(other_sock, command, full_message)
                        
                        #if msg_type != "QC":
                        #    send_to_eve(clients, msg_type, full_message) 
                    else:
                        send(sock, "ERROR2", "Invalid message type.")
                else:
                    send(sock, "ERROR2", "No connected client.")

            elif msg_type == "DISCONNECT":
                try:
                    if clients[client_name]['other']:  # Here we check if 'other' is not None before proceeding
                        other_sock = clients[client_name]['other']
                        other_client_name = next(key for key, value in clients.items() if value['conn'] == other_sock)
                        send(other_sock, "disc", "Your peer has disconnected.")
                        clients[other_client_name]['other'] = None  # Disconnect the other client too
                    send(sock, "disc", "Disconnected successfully.")
                finally:
                    if client_name in clients:
                        clients.pop(client_name)  # Ensure client is removed from the list
                    print(f"{client_name} disconnected.")

        except Exception as e:
            print(f"Error with {client_name} at {addr}: {e}")
            break

    if client_name and client_name in clients:
        clients.pop(client_name)  # Clean up after disconnection
        print(f"{client_name} disconnected.")
    sock.close()


def server():
    host = 'localhost'
    port = 655  
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print("Server listening on port", port)
    
    try:
        while True:
            sock, addr = server_socket.accept()
            threading.Thread(target=client, args=(sock, addr)).start()
    except KeyboardInterrupt:
        print("\nServer stopping")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
