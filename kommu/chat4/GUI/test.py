import socket
import threading
import queue
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from qiskit import QuantumCircuit
from qiskit_ibm_provider import IBMProvider
import qiskit_aer as qe
import base64
import numpy as np

from function import *
from read_file import read_file
from bb84 import *

# Configuration
path_name = "kommu/chat4/token.txt"
token = read_file(path_name)

default_n_bits = 20
HOST = "localhost"
PORT = 6555
client_data = {}


def decode_message(data):
    action, _, content = data.partition(b":")
    return action.decode(), content.decode()


class QuantumChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Client")
        self.geometry("800x600")
        self.message_queue = queue.Queue()
        self.after(100, self.process_messages)

        # Initialisation des données client
        self.client_name = None
        self.other_name = None
        self.basis = None
        self.bits = None
        self.role = None
        self.choice_bit = 0
        self.sock = None
        self.check_bits = None
        self.choice_index = None
        self.response = None

        self.O_basis = []
        self.O_check_bits = []
        self.O_decision = ''
        self.QC = ''
        self.qc = None
        self.O_index = []
        self.qber = 0.0
        self.final_key = []
        self.key = None
        self.compter = 0
        self.n_bits = default_n_bits

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for the chat client."""
        # Connection components
        self.host_label = tk.Label(self, text="Host:")
        self.host_label.grid(row=0, column=0, padx=2, pady=2, sticky='e')
        self.host_entry = tk.Entry(self, width=15)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.grid(row=0, column=1, padx=2, pady=2)

        self.port_label = tk.Label(self, text="Port:")
        self.port_label.grid(row=0, column=2, padx=2, pady=2, sticky='e')
        self.port_entry = tk.Entry(self, width=5)
        self.port_entry.insert(0, '6555')
        self.port_entry.grid(row=0, column=3, padx=2, pady=2)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=2, pady=2)

        # Bit selection component
        self.n_bits_label = tk.Label(self, text="n_bits:")
        self.n_bits_label.grid(row=1, column=1, padx=2, pady=2, sticky='e')
        self.n_bits_entry = tk.Entry(self, width=5)
        self.n_bits_entry.insert(0, str(default_n_bits))
        self.n_bits_entry.grid(row=1, column=2, padx=2, pady=2)

        # Scrollable text area for logs
        self.log_text = scrolledtext.ScrolledText(self, height=15, state='disabled')
        self.log_text.grid(row=2, column=0, columnspan=7, sticky='we', padx=2, pady=5)

        # Clear log button
        self.clear_log_button = tk.Button(self, text="Clear Log", command=self.clear_log)
        self.clear_log_button.grid(row=1, column=4, padx=2, pady=2)

        # Message entry field
        self.message_entry = tk.Entry(self, width=60)
        self.message_entry.grid(row=3, column=0, columnspan=4, padx=2, pady=2)
        self.send_message_button = tk.Button(self, text="Send Message", command=self.send_message, state='disabled')
        self.send_message_button.grid(row=3, column=4, padx=2, pady=2)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            self.connect_button.config(state='disabled')
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.prompt_user_name()
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.display_message(f"Failed to connect: {e}")
            self.sock = None

    def prompt_user_name(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                self.client_name = simpledialog.askstring("Name", "Enter your name:", parent=self)
                if self.client_name:
                    self.send("REGISTER", self.client_name)
                    break
                else:
                    messagebox.showinfo("Info", "User name entry cancelled. You must enter a name to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                    return

    def prompt_partner_name(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                if partner_name := simpledialog.askstring(
                        "Partner", "Enter the name of the client you wish to connect to:", parent=self):
                    self.send("CONNECT", partner_name)
                    time.sleep(2)
                    break
                else:
                    messagebox.showinfo("Info", "You must enter a name to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                    return

    def prompt_role(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                self.role = simpledialog.askstring("Role", f"{self.client_name}, do you want to be the sender or the receiver? (s/r)", parent=self).strip().lower()
                if self.role:
                    self.send("ROLE", self.role)
                    time.sleep(2)
                    break
                else:
                    messagebox.showinfo("Info", "It was cancelled. You must make your choice to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                    return

    def prompt_choice_bit(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                if choice_bit_input := simpledialog.askstring(
                    "Choice Bit",
                    "How many bits do you want to select for the test?: ",
                    parent=self,
                ):
                    self.choice_bit = int(choice_bit_input)
                    self.send("BIT", self.choice_bit)
                    time.sleep(2)
                    break
                else:
                    messagebox.showinfo("Info", "It was cancelled. You must make your choice to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                        return
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid integer value.")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning("Warning", "Maximum attempts reached. Please try again later.")
                    return

    def receive_messages(self):
        while self.sock:
            try:
                if data := self.sock.recv(4096).decode():
                    self.message_queue.put(data)
                else:
                    self.display_message("Server closed the connection.")
                    break
            except Exception as e:
                messagebox.showerror("Error", f"Error receiving data: {e}")
                break
        self.sock.close()

    def display_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.config(state='disabled')

    def display_error(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"ERROR: {message}\n")
        self.log_text.config(state='disabled')

    def clear_log(self):
        """Clear the log text area."""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')

    def process_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            action, content = decode_message(message.encode())
            self.process_server_message(action, content)
        self.after(100, self.process_messages)

    def process_server_message(self, action, content):
        """Traiter les messages du serveur en fonction de leur type."""
        if action == "ERROR":
            messagebox.showerror("Erreur", content)
            self.display_error(content)
            self.prompt_user_name()
        elif action == "REGISTER":
            messagebox.showinfo("Enregistré", "Vous êtes enregistré avec succès.")
            self.display_message(content)
            self.prompt_partner_name()
        elif action == "ERROR_N":
            messagebox.showerror("Erreur de connexion", content)
            self.display_error(content)
            self.prompt_partner_name()
        elif action == "ERROR_Y":
            messagebox.showwarning("Avertissement de connexion", content)
            self.display_error(content)
            self.prompt_partner_name()
        elif action == "ERROR_M":
            messagebox.showerror("Erreur de message", content)
            self.display_error(content)
        elif action == "CONN":
            messagebox.showinfo("Accusé de réception", content)
            self.display_message(content)
            self.prompt_role()
        elif action == "OTHER":
            self.other_name = content
            messagebox.showinfo("Accusé de réception", f"Le nom de l'autre client est : {content}")
            self.display_message(content)
        elif action == "disc":
            self.display_message(content)
            messagebox.showinfo("Déconnexion", "Déconnecté avec succès.")
            self.sock.close()
        elif action == "ROLE":
            if self.role == content:
                messagebox.showinfo("Rôle", "Vous avez choisi le même rôle, veuillez réessayer.")
                self.display_error(content)
                self.prompt_role()
            else:
                messagebox.showinfo("Rôle", ("Vous êtes l'émetteur." if self.role.startswith('s') else "Vous êtes le récepteur."))
                self.display_message(content)
                if self.role.startswith('s'):
                    self.sender_init(self.get_n_bits())
                    self.display_message("fin de sender_init")

        elif action == "basis":           
            self.O_basis = deconcatenate_data(content)
            self.display_message(f"Basis reçu: {self.O_basis} de {self.other_name}")
            if self.role.startswith('s'):
                self.sender_index(self.get_n_bits())
            elif self.role.startswith('r'):
                self.receiver_basis()
        elif action == "check_bits":
            self.O_check_bits = deconcatenate_data(content)
            self.display_message(f"Checking: {self.O_check_bits}")
            
            self.display_message(f"Bits de vérification reçus: {self.O_check_bits}")
            if self.role.startswith('s'):
                self.continue_sender()
            elif self.role.startswith('r'):
                self.receiver_check()
        elif action == "resp":
            self.O_decision = content
            self.display_message(f"Décision de {self.other_name}: {self.O_decision}")
            if self.role.startswith('r'):
                self.continue_receiver()
        elif action == "QC":
            self.QC = content
            self.display_message(f"QC reçu: {self.QC}")
            if self.role.startswith('r'):
                self.receiver_qam(self.get_n_bits())
        elif action == "bit":
            self.choice_bit = int(content)
        elif action == "index":
            self.O_index = deconcatenate_data(content)
            self.display_message(f"Index reçu: {self.O_index}")
            if self.role.startswith('r'):
                self.receiver_index()
        elif action == "MESSAGE":
            sender, encrypted_message = content.split(":>")
            decrypted_message = decrypt_aes(encrypted_message, self.key)
            self.display_message(f"{sender}: {decrypted_message}")

    def get_n_bits(self):
        try:
            return int(self.n_bits_entry.get())
        except ValueError:
            return default_n_bits

    def repeat_process(self):
        """Encapsulate the repeated process until compter > 3."""
        while self.compter < 3:
            # Reset state before each attempt
            self.O_basis = []
            self.O_check_bits = []
            self.O_index = []
            self.qber = 0.0
            self.final_key = []
            self.key = None

            if self.role.startswith('s'):
                self.sender_init(self.get_n_bits())
            self.sender_index(self.get_n_bits())
            self.continue_sender()
            if self.compter >= 3:
                self.send_message_button.config(state='normal')
                messagebox.showinfo("Info", "You can now send secure messages.")
                break
            else:
                messagebox.showinfo("Info", "Repeating the process until the key is secure.")
                self.compter += 1

    def sender_init(self, n_bits):
        """Initialize the sender's quantum circuit and send it to the receiver."""
        self.basis, self.bits = self.initiate_bb84(n_bits, token)
        self.display_message(f"{self.client_name} Bits: {self.bits}")

    def sender_index(self, n_bits):
        """Envoyer l'index et les bits de vérification au récepteur."""
        if not self.O_basis:
            messagebox.showwarning("Warning", "Les bases de l'autre client ne sont pas encore reçues.")
            return

        # Log des informations de base
        self.display_message(f"Basis of {self.other_name}: {self.O_basis}")
        self.display_message(f"{self.client_name} Basis: {self.basis}")
        self.display_message(f"{self.other_name} Basis: {self.O_basis}")

        n_bits = min(n_bits, len(self.basis), len(self.O_basis))

        # Assurer que le choix des bits ne dépasse pas les bits disponibles
        self.prompt_choice_bit()

        try:
            self.choice_index, self.check_bits, self.key = checking(
                nb_bits=n_bits,
                alice_basis=self.basis,
                bob_basis=self.O_basis,
                bits=self.bits,
                bit_choice=self.choice_bit
            )
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        # Envoi consécutif des messages avec un délai
        self.send("INDEX", concatenate_data(self.choice_index))
        self.display_message("Index envoyé.")

        time.sleep(0.1)  # Ajouter un petit délai avant d'envoyer le message suivant
        self.send("CHECK", concatenate_data(self.check_bits))
        self.display_message("Bits de vérification envoyés.")

    def continue_sender(self):
        """Continuer le traitement pour le rôle émetteur"""
        self.response, self.qber, self.final_key = qber_key(self.check_bits, self.O_check_bits, self.choice_index, self.key)
        self.send("RESP", f"{decision(self.response)}")
        self.display_message(f"Décision de {self.other_name}: {self.O_decision}")
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"Final key: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"New key: {self.key}")

            else:
                messagebox.showwarning("Warning", "No final key generated.")
        else:
            messagebox.showinfo("Info", "No valid key. Restarting the process.")

    def receiver_qam(self, n_bits):
        """Prepare the receiver's basis and measure the quantum circuit."""
        IBMProvider.save_account(token, overwrite=True)

        # Receive the quantum circuit
        qc_str = base64.b64decode(self.QC).decode('utf-8')
        self.qc = QuantumCircuit.from_qasm_str(qc_str)

        # Prepare basis
        self.basis, _ = self.generate_bb84_data(nb_bits=n_bits)
        self.send("BASIS", concatenate_data(self.basis))
        self.display_message("Basis Receiver envoyé.")

        # Measure the qubits
        self.qc = bob_measure(self.qc, self.basis)
        self.bits = calcul(self.qc)
        self.display_message(f"{self.client_name} Bits: {self.bits}")
        self.display_message(self.qc.draw())

    def receiver_basis(self):
        """Display the basis received from the other client."""
        self.display_message(f"Basis of {self.other_name}: {self.O_basis}")
        self.display_message(f"{self.client_name} Basis: {self.basis}")
        self.display_message(f"{self.other_name} Basis: {self.O_basis}")

    def receiver_index(self):
        """Envoyer les bits de vérification au sender."""
        choice_index, self.check_bits, self.key = checking(
            nb_bits=self.get_n_bits(),
            alice_basis=self.O_basis,
            bob_basis=self.basis,
            bits=self.bits,
            bit_choice=self.choice_bit,
            choice_index=self.O_index
        )

        self.send("CHECK", concatenate_data(self.check_bits))
        self.display_message("Bits de vérification envoyés.")

    def receiver_check(self):
        """Vérifier le QBER et finaliser la clé."""
        self.response, self.qber, self.final_key = qber_key(self.O_check_bits, self.check_bits, self.O_index, self.key)
        self.send("RESP", f"{decision(self.response)}")
        self.display_message("Réponse envoyée.")

    def continue_receiver(self):
        """Continuer le traitement pour le rôle récepteur"""
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"Final key: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"New key: {self.key}")

                if self.compter >= 3:
                    self.send_message_button.config(state='normal')
                else:
                    messagebox.showinfo("Info", "You must repeat this process at least 3 times to be sure of the integrity of the key.")
                    self.compter += 1

            else:
                messagebox.showwarning("Warning", "No final key generated.")
        else:
            self.compter = 0
            messagebox.showinfo("Info", "No valid key. Restarting the process.")

    def initiate_bb84(self, nb_bits, token):
        """Initiate the BB84 protocol for the sender."""
        basis, bits = self.generate_bb84_data(nb_bits)
        qc = prepare_qubits(bits, basis, token)
        qc_str = qc.qasm()
        qasm_circuit = base64.b64encode(qc_str.encode()).decode('utf-8')

        self.send("QC", qasm_circuit)
        self.display_message("Envois du circuit qc")
        self.send("BASIS", concatenate_data(basis))
        self.display_message("Envois de la base")
        self.display_message(f"{self.client_name} has initiated BB84 with basis {basis} and bits {bits}.")
        return basis, bits

    def generate_bb84_data(self, nb_bits=default_n_bits):
        """Generate random basis and bits for the BB84 protocol."""
        basis = np.random.randint(2, size=nb_bits).tolist()
        bits = np.random.randint(2, size=nb_bits).tolist()
        return basis, bits

    def send_message(self):
        """Send a secure message using the generated key."""
        message_content = self.message_entry.get()
        if message_content and self.key:
            encrypted_message = encrypt_aes(message_content, self.key)
            self.send("MESSAGE", f"{self.client_name}:>{encrypted_message}")
            self.display_message(f"You: {message_content}")
            self.message_entry.delete(0, tk.END)

    def send(self, action, content):
        """Send a message via the socket."""
        message = f"{action}:{content}".encode()
        try:
            self.sock.sendall(message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            if self.sock:
                self.sock.close()
                self.sock = None

    def on_closing(self):
        """Handle the closing event for the window."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.sock:
                self.sock.close()
            self.destroy()


if __name__ == "__main__":
    app = QuantumChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
