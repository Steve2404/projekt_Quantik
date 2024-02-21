import socket
import threading

clients = {}

def handle_client(client_socket, client_address):
    username = client_socket.recv(1024).decode()
    clients[username] = client_socket
    print(f"{username} connecté depuis {client_address}")

    while True:
        message = client_socket.recv(1024).decode()
        if message == 'exit':
            del clients[username]
            client_socket.close()
            break
        print(f"{username}: {message}")
        for client in clients.values():
            if client != client_socket:
                client.sendall(f"{username}: {message}".encode())

# Création d'un socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Liaison du socket à une adresse et un port
    s.bind(('localhost', 12346))
    # Attente de connexions entrantes
    s.listen()
    print("Serveur en attente de connexions...")

    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
