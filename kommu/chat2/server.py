import socket
import threading
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

clients = {}

def handle_client(client_socket, client_address):
    username = client_socket.recv(1024).decode()
    clients[username] = client_socket
    print(f"{username} connecté depuis {client_address}")

    while True:
        message = client_socket.recv(1024)
        if message == b'exit':
            del clients[username]
            client_socket.close()
            break
        print(f"{username}: {message.decode()}")

        for client in clients.values():
            if client != client_socket:
                public_key = serialization.load_pem_public_key(client.recv(4096))
                ciphertext = public_key.encrypt(
                    message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                client.sendall(ciphertext)

# Création d'un socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Liaison du socket à une adresse et un port
    s
