import socket
import threading
from function import *


clients = {}


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
                    send(sock, "ERROR", f"{client_name}:>Name already in use.")

                elif client_name == "Eve":
                    print(f"{client_name} has just logged on ")

                    clients[client_name] = {
                        'conn': sock, 'other': None, 'sender': None, 'steal': 'spion'}
                else:
                    clients[client_name] = {'conn': sock, 'other': None}
                    print(f"{client_name} registered from {addr}")
                    send(sock, "REGISTER",
                         f"{client_name}:>Registered successfully.")

            elif msg_type == "CONNECT":
                target_name = content.strip()

                # Ensure that the target customer exists
                if target_name not in clients:
                    send(sock, "ERROR_N", f"{target_name} not available.")
                else:
                    target_client = clients[target_name]
                    current_client = clients[client_name]

                    # Checks whether the target client is the same as the current client
                    if target_client['conn'] == current_client['conn']:
                        send(sock, "ERROR_Y", "You cannot communicate with yourself.")
                        # Checks whether the current or target client is already connected to someone else
                    elif current_client['other'] is not None or target_client['other'] is not None:
                        if current_client['other'] == target_client['conn']:
                            # If already connected to each other
                            #send(sock, "ACK2", f"{target_name} Is already connected to you.")
                            send(sock, "CONN", f"Connected to {target_name}.")
                            time.sleep(2)
                            send(target_client['conn'], "OTHER", client_name)
                        else:
                            # If already connected but not to each other
                            send(
                                sock, "ERROR_N", f"{target_name} is already connected to someone else.")
                    else:
                        # Connect the two clients
                        current_client['other'] = target_client['conn']
                        target_client['other'] = sock

                        # Send connection confirmations
                        send(sock, "CONN", f"Connected to {target_name}.")
                        time.sleep(2)
                        send(target_client['conn'], "OTHER", client_name)

            # Eve thinks she's the receiver
            elif msg_type == 'ROLE':
                if clients.get('Eve') is not None and content == 's':
                    clients['Eve']['sender'] = clients[client_name]['conn']
                    clients['Eve']['other'] = clients[client_name]['other']

                if other_sock := clients[client_name]['other']:
                    full_message = content
                    send(other_sock, 'ROLE', full_message)
                else:
                    send(sock, "ERROR2", "No connected client.")

            # QC interception by Eve
            elif msg_type == 'QC':
                if clients.get('Eve') is not None and clients['Eve']['steal']:
                    eve_sock = clients['Eve']['conn']
                    send(eve_sock, 'QC', content)
                    clients['Eve']['steal'] = None

                elif other_sock := clients[client_name]['other']:
                    if clients.get('Eve') is not None:
                        clients['Eve']['steal'] = 'spion'
                    full_message = content
                    send(other_sock, 'QC', full_message)
                else:
                    send(sock, "ERROR2", "No connected client.")

            elif msg_type in ["MESSAGE", "BASIS", "INDEX", "CHECK", "RESP", "DECIS", "BIT"]:

                if other_sock := clients[client_name]['other']:
                    # Mapping message types to their corresponding command names on the network
                    message_types = {
                        "MESSAGE": "MESSAGE",
                        "BASIS": "basis",
                        "INDEX": "index",
                        "CHECK": "check_bits",
                        "RESP": "resp",
                        "DECIS": "decis",
                        "BIT": "bit"
                    }
                    if command := message_types.get(msg_type):
                        full_message = f"{client_name}:>{content}" if msg_type == "MESSAGE" else content
                        send(other_sock, command, full_message)
                        send_to_eve(clients, msg_type, full_message)
                    else:
                        send(sock, "ERROR_M", "Invalid message type.")
                else:
                    send(sock, "ERROR_N", "No connected client.")

            elif msg_type == "DISCONNECT":
                try:
                    # Here we check if 'other' is not None before proceeding
                    if clients[client_name]['other']:
                        other_sock = clients[client_name]['other']
                        other_client_name = next(
                            key for key, value in clients.items() if value['conn'] == other_sock)
                        send(other_sock, "disc", "Your peer has disconnected.")
                        # Disconnect the other client too
                        clients[other_client_name]['other'] = None
                    send(sock, "disc", "Disconnected successfully.")
                finally:
                    if client_name in clients:
                        # Ensure client is removed from the list
                        clients.pop(client_name)
                    print(f"{client_name} disconnected.")

        except Exception as e:
            print(f"Error with {client_name} at {addr}: {e}")
            break

    if client_name and client_name in clients:
        clients.pop(client_name)  # Clean up after disconnection
        print(f"{client_name} disconnected.")
    sock.close()


def server():
    host = "localhost"
    port = 6555
    # host = '0.0.0.0'
    # port = 9999

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
