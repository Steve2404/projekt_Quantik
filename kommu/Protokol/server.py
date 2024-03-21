import socket
import threading


# stocker les informations d alice et Bob
client_data = {
    'Alice': {'conn': None, 'bases': None, 'qasm': None},
    'Bob': {'conn': None, 'bases': None}
}

def client(conn, addr):
    global client_data
    client_name = None

    while True:
        try:
            # Reception des donnees
            data = conn.recv(4096).decode()
            print(data)
            if not data: 
                break

            # identifier le client et traiter le message
            if data.startswith('Alice:') or data.startswith('Bob:'):
                client_name = data.split(":")[0]
                client_data[client_name]['conn'] = conn
                if client_name == 'Alice':
                    print(f"Alice connected to {addr}")
                elif client_name == 'Bob':
                    print(f"Bob connected to {addr}")
                    # Si qc est deja reçu par Alice 
                    if client_data['Alice']['qasm'] is not None:
                        conn.sendall(client_data['Alice']['qasm'].encode())
            elif "QASM" in data and client_name == 'Alice':
                # qc envoyé a Bob
                client_data['Alice']['qasm'] = data
                if client_data['Bob']['conn'] is not None:
                    client_data['Bob']['conn'].sendall(data.encode())
            else:
                print(f"Message non reconnu de {addr}: {data}")

        except Exception as e:
            print(f"Erreur avec {client_name} a {addr}: {e}")
            break
    
    # déconnections
    if client_name:
        client_data[client_name] = {'conn': None, 'bases': None, 'qasm': None if client_name == 'Alice' else None}
        print(f"{client_name} déconnecté ....")
    conn.close()

    
def server():
    host = 'localhost'
    port = 655
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    
    print("Serveur en écoute ...")
    
    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Arrêt du Serveur")
    finally:
        server_socket.close()
        

if __name__ == "__main__":
    server()
