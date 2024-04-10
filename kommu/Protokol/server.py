import socket
import threading


# stocker les informations d alice et Bob
client_data = {
    'Alice': {'conn': None, 'basis': None, 'qasm': None, 'bit_choice': None, 'choice_index': None},
    'Bob': {'conn': None, 'basis': None}
}

def client(conn, addr):
    global client_data
    client_name = None

    while True:
        try:
            # Reception des donnees
            data = conn.recv(4096).decode()
            print(f"data= {data}")
            if not data: 
                break

            # identifier le client et traiter le message
            if data.startswith('Alice:') or data.startswith('Bob:'):
                client_name = data.split(":")[0]
                print(f"client_name= {client_name}")
                client_data[client_name]['conn'] = conn
                if client_name == 'Alice':
                    print(f"Alice connected to {addr}")
                    conn.sendall("Attendre Bob".encode())
                elif client_name == 'Bob':
                    print(f"Bob connected to {addr}")
                    # Si qc est deja reçu par Alice 
                    if client_data['Alice']['qasm'] is not None:
                        print("server envois a Bob -- qasm")
                        conn.sendall(client_data['Alice']['qasm'].encode())
                    elif client_data['Alice']['bit_choice'] is not None:
                        print("server envois a Bob -- bit_choice")
                        conn.sendall(client_data['Alice']['bit_choice'].encode())
                    elif client_data['Alice']['choice_index'] is not None:
                        print("server envois a Bob -- choice_index")
                        conn.sendall(client_data['Alice']['choice_index'].encode())
                        
            elif "basis" in data and client_name == 'Alice':
                client_data['Alice']['basis'] = data.split(":")[1]
                print("basis in data -- client_name == Alice")
                if client_data['Bob']['conn'] is not None:
                    print("Server envois basis_alice --- BOB")
                    client_data['Bob']['conn'].sendall(data.encode())
                else:
                    print("Bob pas encore connecte")
                        
            elif "qasm" in data and client_name == 'Alice':
                # qc envoyé a Bob
                client_data['Alice']['qasm'] = data.split(":")[1]
                print("qasm in data -- client_name == Alice")
                if client_data['Bob']['conn'] is not None:
                    print("Server envois qasm_alice --- BOB")
                    client_data['Bob']['conn'].sendall(data.encode())
                else:
                    print("Bob pas encore connecte")
                    
            elif "bit_choice" in data and client_name == 'Alice':
                client_data['Alice']['bit_choice'] = data.split(":")[1]
                print("bit_choice in data -- client_name == Alice")
                if client_data['Bob']['conn'] is not None:
                    print("Server envois bit_choice alice --- BOB")
                    client_data['Bob']['conn'].sendall(data.encode())
                else:
                    print("Bob pas encore connecte")
                    
            elif "choice_index" in data and client_name == 'Alice':
                client_data['Alice']['choice_index'] = data.split(":")[1]
                print("choice_index in data -- client_name == Alice")
                if client_data['Bob']['conn'] is not None:
                    print("Server envois choice_index alice --- BOB")
                    client_data['Bob']['conn'].sendall(data.encode())
                else:
                    print("Bob pas encore connecte")
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
