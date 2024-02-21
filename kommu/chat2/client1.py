import socket
import threading
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def receive_messages(client_socket, private_key):
    while True:
        ciphertext = client_socket.recv(4096)
        message = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(message.decode())

# Création d'un socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connexion au serveur
    s.connect(('localhost', 12346))

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    username = input("Entrez votre nom d'utilisateur: ")
    s.sendall(username.encode())
    s.sendall(serialization.public_key_bytes(private_key.public_key()))

    receive_thread = threading.Thread(target=receive_messages, args=(s, private_key))
    receive_thread.start()

    while True:
        message = input()
        ciphertext = private_key.public_key().encrypt(
                        message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        s.sendall(ciphertext)
        if message == 'exit':
            break

