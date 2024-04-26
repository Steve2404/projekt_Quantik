import socket
import threading
from functions.create_message import create_message, decode_message

client_data = {
    'Alice': {'conn': None, 'basis': None, 'qasm': None, 'bit_choice': None, 'choice_index': None},
    'Bob': {'conn': None, 'basis': None, 'qasm': None, 'bit_choice': None, 'choice_index': None}
}

def client(conn, addr):  # sourcery skip: low-code-quality
    global client_data 
    client_name = None

    while True:
        try:
            data = conn.recv(4096)
            if not data: 
                break

            msg_type, content = decode_message(data)
            if msg_type in ["Alice", "Bob"]:
                client_name = msg_type
                client_data[client_name]['conn'] = conn
                print(f"{client_name} connected from {addr}")
                response = "Connected: Waiting for other party."
                conn.sendall(create_message("ACK", response))
                
            elif msg_type == "QASM":
                print(f"nom du client: {client_name}")
                
                if client_name == "Alice":
                    client_data[client_name]['qasm'] = content
                    print(f"QASM received from {client_name}.")
                      
                    # Server envois le QASM à Bob si Bob est déjà connecté
                    if client_data.get("Bob", {}).get("conn"):
                        client_data["Bob"]["conn"].sendall(create_message("QASM", content))
                        
                        # server envois accuse de reception a Alice: Bonne reception
                        client_data["Alice"]["conn"].sendall(create_message("ACK", "server send QASM to Bob"))
                        
                    else: # server envois accuse de reception a Alice: Bob pas encore connecte
                        print("other Party is not now Available ...")
                        conn.sendall(create_message("AW", "Bob is not yet available ... Wait"))
                        
            elif msg_type == "ACK":
                print(f"nom du client: {client_name}")
                
                if client_name == "Bob":
                    print(f"{client_name}: {content}")
                    if client_data.get("Alice", {}).get("conn"):
                        client_data["Alice"]["conn"].sendall(create_message("ACK", content))    
                         
                    else: # server envois accuse de reception a Bob: Alice pas encore connecte
                        print("other Party is not now Available ...")
                        conn.sendall(create_message("AW", "Alice is not yet available ... Wait"))
                        

            elif msg_type == "Basis":
                if client_name:
                    client_data[client_name]['basis'] = content
                    print(f"Server received Basis from {client_name}.")
                    other_client_name = "Bob" if client_name == "Alice" else "Alice"
                    # Server envois Alice_base a Bob: si bob connecte
                    if client_data.get(other_client_name, {}).get("conn"):
                        client_data[other_client_name]["conn"].sendall(create_message("Basis", content))                       
                        # server envois accuse de reception a Alice: Bonne reception 
                        conn.sendall(create_message("ACK", f"Server sended {client_name} Basis to {other_client_name}")) 
                         
                    else: # server envois accuse de reception a Alice: Bob pas encore connecte
                        print(f"{other_client_name} is not now Available ...")
                        conn.sendall(create_message("AW", f"{other_client_name} is not yet available ... Wait"))
                        
                else:
                    print("client inconnu")
            
            # Gestion des indices de bits choisis pour la vérification
            elif msg_type == "CheckBits":
                if client_name:
                    print(f"Indices for checking received from {client_name}.")
                    other_client_name = "Bob" if client_name == "Alice" else "Alice"
                    
                    if client_data.get(other_client_name, {}).get("conn"):
                        client_data[other_client_name]["conn"].sendall(create_message("CheckBits", content))
                        conn.sendall(create_message("ACK", f"Server sended {client_name}'Indices for checking to {other_client_name}"))
                    else:
                        print("other Party is not now Available ...")
                        conn.sendall(create_message("AW", f"{other_client_name} is not yet available ... Wait"))
 
            # Ajoutez ici plus de cas selon les besoins

        except Exception as e:
            print(f"Erreur avec {client_name} à {addr}: {e}")
            break

    if client_name:
        client_data[client_name] = {'conn': None, 'basis': None, 'qasm': None, 'bit_choice': None, 'choice_index': None}  # Nettoyer après déconnexion
        print(f"{client_name} déconnecté.")
    conn.close()


def server():
    host = 'localhost'
    port = 9999  # Assurez-vous que ce port est le même que celui utilisé par Alice et Bob
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print("Serveur en écoute sur le port", port)
    
    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connexion établie avec {addr}")
            threading.Thread(target=client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
