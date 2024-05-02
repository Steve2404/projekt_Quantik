"""
je voudrais que tu ecrive un code en Qt ou Tkinker pour simuler la communication entre Alice et Bob.
sur l interface on a deux entre une pour host et l autre pour port
ensuite il ya un champ de text ou l utilisateur entre le message(son nom, etc...)
un autre champ pour envoyer le message.
un champ pour recevoir le message(un peu comme dans l invite de commnade)


"""


import threading
import queue

def receive_messages(sock, messages_queue):
    """ Thread pour recevoir les messages et les mettre dans une queue. """
    while True:
        message = sock.recv(1024)  # Exemple de réception de message
        if message:
            messages_queue.put(message.decode())

def main_interaction(sock, name):
    messages_queue = queue.Queue()
    threading.Thread(target=receive_messages, args=(sock, messages_queue), daemon=True).start()
    
    while True:
        # Vérifier si des messages sont disponibles dans la queue
        try:
            while not messages_queue.empty():
                message = messages_queue.get_nowait()
                print(f"\nReceived: {message}\n{name}:> ", end="")  # Afficher le message reçu
        except queue.Empty:
            pass

        # Gérer l'entrée de l'utilisateur dans le thread principal
        user_input = input(f"{name}:> ")
        if user_input.lower() == "quit":
            break
        # Envoyer l'input quelque part, par exemple à un serveur ou à un autre thread

