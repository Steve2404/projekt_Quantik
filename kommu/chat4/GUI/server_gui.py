import socket
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from function import *

clients = {}
server_socket = None
server_thread = None
actions = ["MESSAGE", "BASIS", "INDEX", "CHECK", "RESP", "DECIS", "BIT"]
message_types = {
    "MESSAGE": "MESSAGE",
    "BASIS": "basis",
    "INDEX": "index",
    "CHECK": "check_bits",
    "RESP": "resp",
    "DECIS": "decis",
    "BIT": "bit"
    }


class QuantumChatServer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Server")
        self.geometry("600x400")
        self.server_running = False
        self.host = "localhost"
        self.port = 6555

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components for the server."""
        # Host and port input
        self.host_label = tk.Label(self, text="Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.host_entry = tk.Entry(self, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_label = tk.Label(self, text="Port:")
        self.port_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.port_entry = tk.Entry(self, width=10)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Start/Stop server buttons
        self.start_button = tk.Button(
            self, text="Start Server", command=self.start_server)
        self.start_button.grid(row=1, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(
            self, text="Stop Server", command=self.stop_server, 
            state='disabled')
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            self, height=15, state='disabled')
        self.log_text.grid(
            row=2, column=0, columnspan=4, sticky='we', padx=5, pady=5)

    def start_server(self):
        global server_thread, server_socket
        self.host = self.host_entry.get()
        self.port = int(self.port_entry.get())
        self.display_message("Starting server...")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            self.server_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            server_thread = threading.Thread(target=self.accept_clients)
            server_thread.start()
            self.display_message(
                f"Server listening on {self.host}:{self.port}")
        except Exception as e:
            messagebox.showerror(
                "Server Error", f"Could not start server: {e}")
            self.display_message(f"Error: {e}")

    def stop_server(self):
        global server_socket, server_thread, clients
        self.display_message("Stopping server...")
        self.server_running = False
        if server_socket:
            server_socket.shutdown(socket.SHUT_RDWR)
            server_socket = None
        if server_thread:
            server_thread.join()
        clients.clear()
        self.display_message("Server stopped.")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def display_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.config(state='disabled')

    def accept_clients(self):
        while self.server_running:
            try:
                sock, addr = server_socket.accept()
                threading.Thread(
                    target=self.client_handler, args=(sock, addr)).start()
            except OSError:
                break

    def client_handler(self, sock, addr):
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
                        send(
                            sock, 
                            "ERROR", 
                            f"{client_name} name is already in use."\
                                .replace("<END>", ""))

                    elif client_name == "Eve":
                        clients[client_name] = {
                            'conn': sock, 'other': None, 
                            'sender': None, 'steal': 'Espionnage'}
                    else:
                        clients[client_name] = {'conn': sock, 'other': None}
                        self.display_message(
                            f"{client_name} registered from {addr}"\
                                .replace("<END>", ""))
                        send(sock, "REGISTER", f"{client_name}")

                elif msg_type == "CONNECT":
                    target_name = content.strip()

                    # Ensure that the target customer exists
                    if target_name not in clients:
                        send(
                            sock, 
                            "ERROR_C", 
                            f"{target_name} not available."\
                                .replace("<END>", ""))
                    else:
                        target_client = clients[target_name]
                        current_client = clients[client_name]
                        message = f"{target_name}:Connected to {target_name}."\
                            .replace("<END>", "")

                        # Checks whether the target client is the same 
                        # as the current client
                        if target_client['conn'] == current_client['conn']:
                            send(
                                sock, 
                                "ERROR_C", 
                                "You cannot communicate with yourself.")
                        elif (current_client['other'] is not None or 
                              target_client['other'] is not None):
                            if (current_client['other'] 
                                == target_client['conn']):
                                send(sock, "CONN", message)
                            else:
                                send(
                                    sock, 
                                    "ERROR_C", 
                                    f"{target_name} is already connected to "\
                                        "someone else.".replace("<END>", ""))
                        else:
                            current_client['other'] = target_client['conn']
                            target_client['other'] = sock
                            send(sock, "CONN", message)

                elif msg_type == 'ROLE':
                    content = content.replace("<END>","")
                    if clients.get('Eve') is not None and content == 's':
                        clients['Eve']['sender'] = clients[client_name]['conn']
                        clients['Eve']['other'] = clients[client_name]['other']

                    if other_sock := clients[client_name]['other']:
                        send(other_sock, 'ROLE', content)
                    else:
                        send(sock, "ERROR_C", "No connected client.")
                        
                elif msg_type == 'BACKEND':
                    if other_sock := clients[client_name]['other']:
                        send(other_sock, 'BACKEND', content)
                    else:
                        send(sock, "ERROR_C", "No connected client.")
                elif msg_type == 'RESTART':
                    if other_sock := clients[client_name]['other']:
                        send(other_sock, 'RESTART', content)
                    else:
                        send(sock, "ERROR_C", "No connected client.")

                elif msg_type == 'QC':
                    
                    if (clients.get('Eve') is not None and 
                        clients['Eve']['steal']):
                        eve_sock = clients['Eve']['conn']
                        send(eve_sock, 'QC', content)
                        clients['Eve']['steal'] = None
                    elif other_sock := clients[client_name]['other']:
                        if clients.get('Eve') is not None:
                            clients['Eve']['steal'] = 'Espionnage'
                        send(other_sock, 'QC', content)
                    else:
                        send(sock, "ERROR_C", "No connected client.")

                elif msg_type in actions:
                    if other_sock := clients[client_name]['other']: 
                        if command := message_types.get(msg_type):
                            send(other_sock, command, content)
                            send_to_eve(clients, command, content)
                        else:
                            send(sock, "ERROR_M", "Invalid message type.")
                    else:
                        send(sock, "ERROR_C", "No connected client.")
                        
                elif msg_type == "Exception":
                    if clients[client_name]['other']:
                        other_sock = clients[client_name]['other']
                        send(other_sock, "Exception", content)
                    else:
                        send(sock, "ERROR_C", "No connected client.")
                
                elif msg_type == "DISCONNECT":
                    try:
                        if clients[client_name]['other']:
                            other_sock = clients[client_name]['other']
                            other_client_name = next(
                                key for key, value in clients.items() 
                                if value['conn'] == other_sock)
                            send(other_sock, "disc", content)
                            clients[other_client_name]['other'] = None
                        send(sock, "disc_ack", "Disconnected from the server.")
                    finally:
                        if client_name in clients:
                            clients.pop(client_name)
                        self.display_message(
                            f"{client_name} disconnected."\
                                .replace("<END>", ""))

            except Exception as e:
                self.display_message(
                    f"Error with {client_name} at {addr}: {e}"\
                        .replace("<END>", ""))
                break

        if client_name and client_name in clients:
            clients.pop(client_name)
            self.display_message(
                f"{client_name} disconnected.".replace("<END>", ""))
        sock.close()


if __name__ == "__main__":
    app = QuantumChatServer()
    app.mainloop()
