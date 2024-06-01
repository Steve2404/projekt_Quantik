import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps
import base64
import queue
import numpy as np

from bb84 import intercept_measure
from read_file import read_file
from function import *

# Configuration
path_name = "kommu/chat4/token.txt"
token = read_file(path_name)
default_n_bits = 20
HOST = "localhost"
PORT = 6555
client_name = 'Eve'


def decode_message(data):
    action, _, content = data.partition(b":")
    return action.decode(), content.decode()


class QuantumSpyClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Spy Client - Eve")
        self.geometry("800x600")
        self.sock = None
        self.nb_bits = default_n_bits
        self.message_queue = queue.Queue()
        self.base = np.random.randint(2, size=self.nb_bits)

        self.setup_ui()
        self.after(100, self.process_messages)

    def setup_ui(self):
        """Set up the user interface for the spy client."""
        # Host and Port
        self.host_label = tk.Label(self, text="Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.host_entry = tk.Entry(self, width=15)
        self.host_entry.insert(0, HOST)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_label = tk.Label(self, text="Port:")
        self.port_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.port_entry = tk.Entry(self, width=10)
        self.port_entry.insert(0, str(PORT))
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Number of Bits
        self.nb_bits_label = tk.Label(self, text="nb_bits:")
        self.nb_bits_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.nb_bits_entry = tk.Entry(self, width=5)
        self.nb_bits_entry.insert(0, str(self.nb_bits))
        self.nb_bits_entry.grid(row=1, column=1, padx=5, pady=5)

        # Connect/Disconnect buttons
        self.connect_button = tk.Button(
            self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        self.disconnect_button = tk.Button(
            self, text="Disconnect", command=self.disconnect_from_server, 
            state='disabled')
        self.disconnect_button.grid(row=0, column=5, padx=5, pady=5)

        # Clear Log Button
        self.clear_button = tk.Button(
            self, text="Clear Log", command=self.clear_log)
        self.clear_button.grid(row=0, column=6, padx=5, pady=5)

        # Log Text Area
        self.log_text = scrolledtext.ScrolledText(
            self, height=15, state='disabled')
        self.log_text.grid(
            row=2, column=0, columnspan=7, sticky='we', padx=5, pady=5)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.nb_bits = int(self.nb_bits_entry.get())
        self.base = np.random.randint(2, size=self.nb_bits)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            self.send("REGISTER", client_name)
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.display_message(f"Connected to {host}:{port}")
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.display_message(f"Failed to connect: {e}")
            self.sock = None

    def disconnect_from_server(self):
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock = None
            self.connect_button.config(state='normal')
            self.disconnect_button.config(state='disabled')
            self.display_message("Disconnected from the server.")

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, 'end')
        self.log_text.config(state='disabled')

    def receive_messages(self):
        buffer = ""
        while self.sock:
            try:
                if data := self.sock.recv(4096).decode():
                    buffer += data
                    while "<END>" in buffer:
                        message, buffer = buffer.split("<END>", 1)
                        self.message_queue.put(message)
                else:
                    self.display_message("Server closed the connection.")
                    break
            except Exception as e:
                messagebox.showerror("Error", f"Error receiving data: {e}")
                break
        if self.sock:
            self.sock.close()

    def process_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            action, content = decode_message(message.encode())
            self.process_server_message(action, content)
        self.after(100, self.process_messages)

    def process_server_message(self, action, content):
        if action == "QC":
            
            qc_str = base64.b64decode(content).decode('utf-8')
            qc = QuantumCircuit.from_qasm_str(qc_str)
            qc = intercept_measure(qc, self.base)
            #self.display_message(qc.draw())
            qc_str = dumps(qc)
            qc_qasm = base64.b64encode(qc_str.encode()).decode('utf-8')
            self.send("QC", qc_qasm)
            self.display_message("Sending intercepted QC to server")
        else:
            self.display_message(f"Received message: {action}: {content}"\
                .replace("<END>", ""))

    def display_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.config(state='disabled')

    def send(self, action, content):
        message = f"{action}:{content}"
        try:
            self.sock.sendall(message.encode())
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to send message: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None


if __name__ == "__main__":
    app = QuantumSpyClient()
    app.mainloop()
