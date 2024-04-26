import socket
import threading
from function import decode_message, send

clients = {}
token = read_file2("Quantum/projekt_Quantik/kommu/chat4/token.txt")
qc_bell = create_bell_state(token)

def client(sock, addr):  
    global clients
    client_name = None

    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break

            msg_type, content = decode_message(data)
            if msg_type == "REGISTER":
                client_name = content
                if client_name in clients:
                    send(sock, "ERROR", f"{client_name} is already in use.")
                else:
                    clients[client_name] = {'conn': sock, 'other': None}
                    print(f"{client_name} registered from {addr}")
                    send(sock, "REGISTER", "Registered successfully.")

            elif msg_type == "CONNECT":
                target_name = content.strip()
                if target_name not in clients:
                    send(sock, "ERROR2", f"{target_name} not available.")
                else:
                    establish_connection(client_name, target_name, sock)

            elif client_name == 'Eve':
                handle_eve_interception(msg_type, content, client_name)

            elif msg_type in ["MESSAGE", "ROLE", "QC", "BASIS", "INDEX", "CHECK", "RESP", "BIT"]:
                handle_messages(client_name, msg_type, content)

            elif msg_type == "DISCONNECT":
                disconnect_client(client_name, sock)

        except Exception as e:
            print(f"Error with {client_name} at {addr}: {e}")
            break

    cleanup_client(client_name)
    sock.close()

def establish_connection(client_name, target_name, sock):
    target_client = clients[target_name]
    current_client = clients[client_name]

    if target_client['conn'] == current_client['conn']:
        send(sock, "ERROR2", "Cannot communicate with yourself.")
    elif current_client['other'] is not None or target_client['other'] is not None:
        send(sock, "ERROR2", f"{target_name} is already connected to someone else.")
    else:
        # Connect clients
        current_client['other'] = target_client['conn']
        target_client['other'] = sock
        send(sock, "ACK", f"Connected to {target_name}.")
        send(target_client['conn'], "OTHER", client_name)

def handle_eve_interception(msg_type, content, client_name):
    if msg_type == "QC":
        forward_to_bob(client_name, content)

def handle_messages(client_name, msg_type, content):
    other_sock = clients[client_name]['other']
    if other_sock:
        send(other_sock, msg_type, content)
    else:
        send(clients[client_name]['conn'], "ERROR2", "No connected client.")

def forward_to_bob(eve_name, content):
    for client in clients.values():
        if client['name'] == 'Bob':
            send(client['conn'], "QC", content)

def disconnect_client(client_name, sock):
    if clients[client_name]['other']:
        other_client_name = next(key for key, value in clients.items



def handle_eve_interception(msg_type, content, eve_sock):
    # Eve reçoit des copies de tous les messages QC passant par le serveur
    if msg_type == "QC":
        # Envoyer le contenu à Eve pour inspection
        send(eve_sock, 'QC', content)
        # Ensuite, retransmettre le message aux destinataires appropriés
        retransmit_to_other_clients(content)

def retransmit_to_other_clients(content):
    # Trouver le client destinataire original si nécessaire ou simplement retransmettre à tous sauf à Eve
    for client_name, info in clients.items():
        if client_name != 'Eve':  # Assurez-vous de ne pas renvoyer à Eve
            send(info['conn'], 'QC', content)


def client(sock, addr):  
    global clients
    client_name = None

    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break

            msg_type, content = decode_message(data)
            if msg_type == "REGISTER":
                client_name = content
                clients[client_name] = {'conn': sock, 'other': None}
                print(f"{client_name} registered from {addr}")
                send(sock, "REGISTER", "Registered successfully.")

            elif msg_type == "QC" and 'Eve' in clients:
                # Supposons qu'Eve est déjà connectée et identifiée dans `clients`
                handle_eve_interception(msg_type, content, clients['Eve']['conn'])

            # Gérer les autres types de messages ici ...

        except Exception as e:
            print(f"Error with {client_name} at {addr}: {e}")
            break

    if client_name in clients:
        clients.pop(client_name)
    sock.close()

