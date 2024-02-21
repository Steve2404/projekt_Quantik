import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            if message := client_socket.recv(1024).decode():
                print(message)
            else:
                break
        except OSError as e:
            print("Erreur de réception de message:", e)
            break

# Création d'un socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connexion au serveur
    s.connect(('localhost', 12346))

    username = input("Entrez votre nom d'utilisateur: ")
    s.sendall(username.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(s,))
    receive_thread.start()

    while True:
        message = input()
        s.sendall(message.encode())
        if message == 'exit':
            break
