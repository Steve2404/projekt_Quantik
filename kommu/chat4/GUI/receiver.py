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
        self.n_bits_label.grid(row=1, column=0, padx=2, pady=2, sticky='e')
        self.n_bits_entry = tk.Entry(self, width=5)
        self.n_bits_entry.insert(0, str(default_n_bits))
        self.n_bits_entry.grid(row=1, column=1, padx=2, pady=2)

        # Scrollable text area for logs
        self.log_text = scrolledtext.ScrolledText(self, height=15, state='disabled')
        self.log_text.grid(row=3, column=0, columnspan=7, sticky='we', padx=2, pady=5)

        # Clear log button
        self.clear_log_button = tk.Button(self, text="Clear Log", command=self.clear_log)
        self.clear_log_button.grid(row=2, column=4, padx=2, pady=2)
        
        # Disconnect button
        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect, state='disabled')
        self.disconnect_button.grid(row=1, column=4, padx=2, pady=2)
        
        # repeat action
        self.repeat_button = tk.Button(self, text="Repeat", command=self.restart_protocol, state='normal')
        #self.repeat_button.grid(row=1, column=3, padx=2, pady=2)
        self.repeat_button.grid_remove()
        
        # attempt
        self.attempt_label = tk.Label(self, text="Attempt:")
        self.attempt_label.grid(row=2, column=1, padx=2, pady=2, sticky='e')
        self.attempt_entry = tk.Entry(self, width=4, state='normal')
        self.attempt_entry.insert(0, '0')
        self.attempt_entry.config(state='disabled')
        self.attempt_entry.grid(row=2, column=2, padx=2, pady=2)
        
    
        

        # Message entry field
        self.message_entry = tk.Entry(self, width=60)
        self.message_entry.grid(row=4, column=0, columnspan=4, padx=2, pady=2)
        self.send_message_button = tk.Button(self, text="Send Message", command=self.send_message, state='disabled')
        self.send_message_button.grid(row=4, column=4, padx=2, pady=2)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
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
                    #time.sleep(2)
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
                    #time.sleep(2)
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
                    #time.sleep(2)
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
        if self.sock:
            self.sock.close()

    def display_attempt(self, number):
        self.attempt_entry.config(state='normal')
        self.attempt_entry.insert('end', str(number))
        self.attempt_entry.config(state='disabled')

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
            messagebox.showinfo("Saved", "You have been successfully registered.")
            self.display_message(content)
            self.prompt_partner_name()
        elif action == "ERROR_N":
            messagebox.showerror("Connection error", content)
            self.display_error(content)
            self.prompt_partner_name()
        elif action == "ERROR_Y":
            messagebox.showwarning("Connection warning", content)
            self.display_error(content)
            self.prompt_partner_name()
        elif action == "ERROR_M":
            messagebox.showerror("Message error", content)
            self.display_error(content)
        elif action == "CONN":
            messagebox.showinfo("Acknowledgement", content)
            self.display_message(content)
            self.prompt_role()
        elif action == "OTHER":
            self.other_name = content
            #messagebox.showinfo("Acknowledgment", f"he name of the other client is : {content}")
            self.display_message(content)
        elif action == "disc":
            self.display_message(content)
            messagebox.showinfo("Disconnection", "Disconnected successfully")
            if self.sock:
                self.sock.close()
        elif action == "ROLE":
           #if not self.role:
           #    self.role = simpledialog.askstring("Role", f"{self.client_name}, do you want to be the sender or the receiver? (s/r)", parent=self).strip().lower()
           #
            if self.role == content:
                messagebox.showinfo("Role", "You have selected the same role, please try again.")
                self.display_error(content)
                self.prompt_role()
            else:
                messagebox.showinfo("Role", ("You are the sender." if self.role.startswith('s') else "You are the receiver."))
                self.display_message(content)
                if self.role.startswith('s'):
                    self.sender_init(self.get_n_bits())
            
        elif action == "basis":           
            self.O_basis = deconcatenate_data(content)
            self.display_message(f"Basis received: {self.O_basis} of {self.other_name}")
            if self.role.startswith('s'):
                self.sender_index()
            elif self.role.startswith('r'):
                self.receiver_basis()
        elif action == "check_bits":
            self.display_message(f"checking bits: {content}")
            self.O_check_bits = deconcatenate_data(content)
            self.display_message(f"check bit received: {self.O_check_bits} of {self.other_name}")

            if self.role.startswith('s'):
                self.continue_sender()
            elif self.role.startswith('r'):
                self.receiver_check()
        elif action == "resp":
            self.O_decision = content
            self.display_message(f"Decision of {self.other_name}: {self.O_decision}")
            if self.role.startswith('r'):
                self.continue_receiver()
        elif action == "QC":
            self.QC = content
            if self.role.startswith('r'):
                self.receiver_qam(self.get_n_bits())
        elif action == "bit":
            self.choice_bit = int(content)
        elif action == "index":
            self.O_index = deconcatenate_data(content)
            self.display_message(f"index of {self.other_name}: {self.O_index}")
            if self.role.startswith('r'):
                self.receiver_index()
        elif action == "MESSAGE":
            sender, encrypted_message = content.split(":>")
            decrypted_message = decrypt_aes(encrypted_message, self.key)
            self.display_message(f"{sender}: {decrypted_message}")

    def restart_protocol(self):
        """Restart the protocol process from the beginning."""
        # Reset the relevant variables
        self.O_basis = []
        self.O_check_bits = []
        self.O_index = []
        self.qber = 0.0
        self.final_key = []
        self.key = None

        if self.role.startswith('s'):
            self.sender_init(self.get_n_bits())
        


    def get_n_bits(self):
        try:
            return int(self.n_bits_entry.get())
        except Exception:
            return default_n_bits

    def sender_init(self, n_bits):
        
        self.basis, self.bits = self.initiate_bb84(n_bits, token)
        self.display_message(f"{self.client_name} Bits: {self.bits}")

    def sender_index(self):
        if not self.O_basis:
            messagebox.showwarning("Warning", "The basics of the other client have not been received yet.")
            #time.sleep(2)

        # Log des informations de base
        self.display_message(f"Basis of {self.other_name}: {self.O_basis}")
        self.display_message(f"{self.client_name} Basis: {self.basis}")
        self.display_message(f"{self.other_name} Basis: {self.O_basis}")

        
        
        while True:
            # Assurer que le choix des bits ne dépasse pas les bits disponibles
            self.prompt_choice_bit()
            try:
                self.choice_index, self.check_bits, self.key = checking(
                    nb_bits=self.get_n_bits(),
                    alice_basis=self.basis,
                    bob_basis=self.O_basis,
                    bits=self.bits,
                    bit_choice=self.choice_bit
                )
                break
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
                

        # Envoi consécutif des messages avec un délai
        self.send("INDEX", concatenate_data(self.choice_index))

        #time.sleep(0.1)  # Ajouter un petit délai avant d'envoyer le message suivant
        self.send("CHECK", concatenate_data(self.check_bits))
    

    def continue_sender(self):
        try:
            self.response, self.qber, self.final_key = qber_key(self.check_bits, self.O_check_bits, self.choice_index, self.key)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            
        self.send("RESP", f"{decision(self.response)}")
        
        #activate the button
        self.repeat_button.grid(row=1, column=3, padx=2, pady=2)
        #self.repeat_button.config(state='normal')
        
        self.display_attempt(self.compter)
        
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"Final key: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"New key: {self.key}")
                self.compter = 4

                if self.compter >= 2:
                    self.send_message_button.config(state='normal')
                    self.repeat_button.config(state='disabled')
                    self.clear_log()
                else:
                    messagebox.showinfo("Info", f"You must repeat this process at least {3-self.compter} times to be sure of the integrity of the key.")
                    self.compter += 1
                    

            else:
                messagebox.showwarning("Warning", "No final key generated.")
        else:
            self.compter = 0
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
    
        while True:
            try:
                choice_index, self.check_bits, self.key = checking(
                    nb_bits=self.get_n_bits(),
                    alice_basis=self.O_basis,
                    bob_basis=self.basis,
                    bits=self.bits,
                    bit_choice=self.choice_bit,
                    choice_index=self.O_index
                )
                break
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
                time.sleep(2)

        self.send("CHECK", concatenate_data(self.check_bits))


    def receiver_check(self):
        try:
            self.response, self.qber, self.final_key = qber_key(self.O_check_bits, self.check_bits, self.O_index, self.key)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        
        self.send("RESP", f"{decision(self.response)}")

    def continue_receiver(self):
        self.display_attempt(self.compter)
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"Final key: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"New key: {self.key}")
                self.compter = 4

                if self.compter >= 2:
                    self.send_message_button.config(state='normal')
                    self.clear_log()
                else:
                    messagebox.showinfo("Info", f"You must repeat this process at least {3-self.compter} times to be sure of the integrity of the key.")
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
    
        self.send("BASIS", concatenate_data(basis))
    
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
            self.send("MESSAGE", f"{encrypted_message}")
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
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.sock:
                self.sock.close()
            self.destroy()

    def disconnect(self):
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock = None
            self.connect_button.config(state='normal')
            self.disconnect_button.config(state='disabled')
            self.display_message("Disconnected from the server.")
            self.send_message_button.config(state='disabled')

if __name__ == "__main__":
    app = QuantumChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
