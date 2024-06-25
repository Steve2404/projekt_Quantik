import socket
import threading
import queue
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps
from qiskit_ibm_provider import IBMProvider
import base64
import numpy as np

from function import *
from read_file import read_file
from bb84 import *

# windows
path_name = "Quantum/projekt_Quantik/kommu/chat4/GUI/token.txt"
#path_name = "token/token.txt"

# ubuntu
#path_name = "kommu/chat4/GUI/token.txt"
#token = read_file("token.txt")


token = read_file(path_name)

default_n_bits = 20
max_attempts = 3
HOST = "localhost"
PORT = 6555



class QuantumChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Client")
        self.geometry("800x600")
        self.running = True
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
        self.O_response = None
        self.receiving_data = False
        self.restart = False
        self.click = False

        self.O_basis = []
        self.O_check_bits = []
        self.QC = ''
        self.qc = None
        self.O_index = []
        self.qber = 0.0
        self.final_key = []
        self.key = None
        self.compter = 1
        self.n_bits = default_n_bits
        self.backend = "qasm_simulator"

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

        self.connect_button = tk.Button(self, text="Connect", 
                                        command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=2, pady=2)

        # Bit selection component
        self.n_bits_label = tk.Label(self, text="n_bits:")
        self.n_bits_label.grid(row=1, column=0, padx=2, pady=2, sticky='e')
        self.n_bits_entry = tk.Entry(self, width=5)
        self.n_bits_entry.insert(0, str(default_n_bits))
        self.n_bits_entry.grid(row=1, column=1, padx=2, pady=2)

        # Scrollable text area for logs
        self.log_text = scrolledtext.ScrolledText(self, height=15, 
                                                  state='disabled')
        self.log_text.grid(row=3, column=0, columnspan=7, 
                           sticky='we', padx=2, pady=5)

        # Clear log button
        self.clear_log_button = tk.Button(self, text="Clear Log", 
                                          command=self.clear_log)
        self.clear_log_button.grid(row=2, column=4, padx=2, pady=2)
        
        # Disconnect button
        self.disconnect_button = tk.Button(self, text="Disconnect", 
                                           command=self.disconnect, 
                                           state='disabled')
        self.disconnect_button.grid(row=1, column=4, padx=2, pady=2)
        
        # repeat action
        self.repeat_button = tk.Button(self, text="Repeat", 
                                       command=self.restart_protocol, 
                                       state='normal')
        #self.repeat_button.grid(row=1, column=3, padx=2, pady=2)
        self.repeat_button.grid_remove()
        
        # attempt
        self.attempt_label = tk.Label(self, text="Attempt:")
        self.attempt_label.grid(row=2, column=1, padx=2, pady=2, sticky='e')
        self.attempt_entry = tk.Entry(self, width=4, state='normal')
        self.attempt_entry.insert(0, '1')
        self.attempt_entry.config(state='disabled')
        self.attempt_entry.grid(row=2, column=2, padx=2, pady=2)
        
        # Message entry field
        self.message_entry = tk.Entry(self, width=60)
        self.message_entry.grid(row=4, column=0, columnspan=4, padx=2, pady=2)
        self.send_message_button = tk.Button(self, 
                                             text="Send Message", 
                                             command=self.send_message, 
                                             state='disabled')
        self.send_message_button.grid(row=4, column=4, padx=2, pady=2)

    def connect_to_server(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                messagebox.showwarning("Warning", 
                                        f"Error closing old socket: {e}")
        
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            
            if (hasattr(self, 'receiver_thread') and 
               self.receiver_thread.is_alive()):
                self.running = False  # Tell the old thread to stop.
                self.receiver_thread.join()
                
            self.running = True
            self.receiver_thread = threading.Thread(
                                                 target=self.receive_messages, 
                                                 daemon=True)
            self.receiver_thread.start()
            
            self.prompt_user_name()
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.display_message(f"Failed to connect: {e}")
            self.sock = None
    
    def prompt_user_name(self):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                self.client_name = simpledialog.askstring(
                    "Name", 
                    "Enter your name:", 
                    parent=self).strip().capitalize()
                if self.client_name:
                    self.send("REGISTER", self.client_name)
                    break
                else:
                    messagebox.showinfo(
                        "Info", 
                        "User name entry cancelled. You must enter a name "\
                        "to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                        self.disconnect()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                    self.disconnect()

    def prompt_partner_name(self):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                if partner_name := simpledialog.askstring(
                        "Partner", 
                        "Enter the name of the client you wish to connect to:", 
                         parent=self).strip().capitalize():
                    
                    self.send("CONNECT", partner_name)
                    break
                else:
                    messagebox.showinfo(
                        "Info", 
                        "You must enter a name to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                        self.disconnect()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                    self.disconnect()

    def prompt_role(self):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                self.role = simpledialog.askstring(
                "Role", 
                f"{self.client_name}, do you want to be the sender or the "\
                    "receiver? (s/r)", 
                    parent=self).strip().lower()
                if self.role:
                    self.send("ROLE", self.role)
                    break
                else:
                    messagebox.showinfo(
                        "Info", 
                        "It was cancelled. You must make your choice "\
                        "to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                        self.disconnect()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                    self.disconnect()

    def prompt_choice_bit(self):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                if choice_bit_input := simpledialog.askstring(
                    "Choice Bit",
                    "How many bits do you want to select for the test?: ",
                    parent=self,
                ):
                    self.choice_bit = int(choice_bit_input)
                    self.send("BIT", self.choice_bit)
                    break
                else:
                    messagebox.showinfo(
                        "Info", 
                        "It was cancelled. You must make your choice "\
                        "to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached.Please try again later.")
                        self.disconnect()
            except ValueError:
                messagebox.showwarning(
                    "Warning", 
                    "Please enter a valid integer value.")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                    self.disconnect()
                
    def prompt_backend(self):
        attempts = 0
        while attempts < max_attempts and self.running:
            try:
                if self.backend in ["simulator_mps", "qasm_simulator"]:
                    break
                self.backend = simpledialog.askstring(
                "Backend Change",
                "The backend is unavailable, switch to a different backend: ",
                    parent=self,
                )
                if self.backend:
                    self.send("BACKEND", self.backend)
                    break

                else:
                    messagebox.showinfo(
                        "Info", 
                        "It was cancelled. You must enter a name to continue.")
                    attempts += 1
                    if attempts >= max_attempts:
                        messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached.Please try again later.")
                        self.disconnect()
            except Exception:
                messagebox.showwarning(
                    "Warning", 
                    "Please enter a valid integer value.")
                attempts += 1
                if attempts >= max_attempts:
                    messagebox.showwarning(
                        "Warning", 
                        "Maximum attempts reached. Please try again later.")
                    self.disconnect()

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                if data := self.sock.recv(4096).decode():
                    self.receiving_data = True
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

    def display_attempt(self, number):
        self.attempt_entry.config(state='normal')
        self.attempt_entry.delete(0, 'end')
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
        self.receiving_data = False
        self.after(100, self.process_messages)

    def process_server_message(self, action, content):
        if action == "ERROR":
            messagebox.showerror("Error", content)
            self.display_error(content)
            self.prompt_user_name()
        elif action == "ERROR_C":
            messagebox.showwarning("Connection failed", content)
            self.display_error(f"Error: {content}")
            self.prompt_partner_name()
        elif action == "ERROR_M":
            messagebox.showerror("Message error", content)
            self.display_error(content)
        elif action == "disc":
            self.display_message(content)
            messagebox.showinfo("Disconnection", content)
            
        elif action == "Exception":
            self.display_message(content)
            messagebox.showerror("Exception", content)
            if self.role.startswith("s"):
                self.restart_protocol()
                
        elif action == "BACKEND":
            if self.role.startswith("s"):
                self.display_message(f"The new Backend is: {content}")
                messagebox.showinfo(
                    'info',
                    f"The new Backend is: {content}"
                )
                self.restart_protocol()
                
        elif action == "RESTART":
            if self.role.startswith("s"):
                messagebox.showinfo(
                    "Restarting",
                    f"{self.other_name} confirmed the restart of the protocol."
                )
                self.restart = True
                self.restart_protocol()
                
            elif self.role.startswith("r"):
                messagebox.showinfo(
                    "Restarting",
                    f"{self.other_name} wants to restart the protocol."
                )
                self.restart = True
                self.restart_protocol()
                self.send("RESTART", "We are restarting the protocol !")
            
        elif action == "disc_ack":
            self.display_message(content)
            if self.sock:
                self.sock.close()

        elif action == "REGISTER":
            messagebox.showinfo("Registration", 
                                "You have been successfully registered.")
            self.display_message(f"Your name is: {content}")
            self.prompt_partner_name()

        elif action == "CONN":
            self.other_name, message = content.split(":")
            messagebox.showinfo("Acknowledgement", message)
            self.display_message(f"Your Partner Name is: {self.other_name}")
            self.display_message(f"Ack: {message}")
            self.prompt_role()
            
        elif action == "ROLE": 
            init_db()   
            if self.role == content:
                messagebox.showinfo(
                    "Role", 
                    "You have selected the same role, please try again.")
                self.display_error(content)
                self.prompt_role()
            else:
                self.display_message(
                    f"{self.client_name}: You are the sender." 
                    if self.role.startswith('s') else 
                    f"{self.client_name}: You are the receiver.")
                messagebox.showinfo(
                    "Role", 
                    ("You are the sender." 
                     if self.role.startswith('s') else 
                     "You are the receiver."))
                if self.role.startswith('s'):
                    if existing_key := get_key(
                        self.client_name, self.other_name):
                        self.key = existing_key
                        messagebox.showinfo(
                            "Info",
                            f"Using existing key for {self.other_name}")
                        self.send_message_button.config(state='normal')
                        self.clear_log()
                        return
                    self.sender_init(self.get_n_bits())
                elif self.role.startswith('r'): 
                    if existing_key := get_key(
                        self.other_name, self.client_name):
                        self.key = existing_key
                        messagebox.showinfo(
                            "Info",
                            f"Using existing key for {self.other_name}")
                        self.send_message_button.config(state='normal')
                        self.clear_log()
                        return

        elif action in ["basis", "BASIS"]:           
            self.O_basis = deconcatenate_data(content)
            if self.role.startswith('s'):
                self.sender_index()
            elif self.role.startswith('r'):
                self.receiver_basis()
        elif action in ["check_bits", "CHECK"]:
            self.O_check_bits = deconcatenate_data(content)

            if self.role.startswith('s'):
                self.display_message(
                    f"Your checking bits is: {self.check_bits}")
                self.display_message(
                    f"{self.other_name} checking bits: {self.O_check_bits}")
                self.sender_check()
            elif self.role.startswith('r'):
                self.display_message(f"Your checking bits: {self.check_bits}")
                self.display_message(
                    f"{self.other_name} checking bits: {self.O_check_bits}")
                self.receiver_check()
        elif action == "resp":
            self.O_response = content
            if self.role.startswith('s'):
                self.continue_sender()
                
            elif self.role.startswith('r'):
                self.continue_receiver()

        elif action == "QC":
            self.QC = content
            if self.role.startswith('r'):
                self.receiver_qam(self.get_n_bits())
                
        elif action == "bit":
            self.choice_bit = int(content)
            
        elif action == "index":
            self.O_index = deconcatenate_data(content)
            self.display_message(
                f"The chosen indexes by {self.other_name} are: {self.O_index}")
            if self.role.startswith('r'):
                self.receiver_index()
                
        elif action == "MESSAGE":
            decrypted_message = decrypt_aes(content, self.key)
            self.display_message(f"{self.other_name}: {decrypted_message}")

    def restart_protocol(self):
        self.display_attempt(self.compter)
        messagebox.showinfo(
            'info',
            'We are restarting the protocol.'
        ) 
        if self.role.startswith('s') and not self.restart:
            self.send("RESTART", "We are restarting the protocol !")
            return 
        
        self.clear_log()
        self.display_message("Reinitializing .....")
        
        self.restart = False
        self.O_basis = []
        self.basis = None
        self.O_check_bits = []
        self.check_bits = None
        self.O_index = []
        self.choice_bit = 0
        self.qber = 0.0
        self.final_key = []
        self.key = None
        self.bits = None
        self.QC = ''
        self.qc = None
        self.O_index = []
        self.choice_index = None
        self.response = None
        self.O_response = None
        
         
        if self.role.startswith('s'):
            self.sender_init(self.get_n_bits())
       

    def get_n_bits(self):
        try:
            return int(self.n_bits_entry.get())
        except Exception:
            return default_n_bits
        

    def sender_init(self, n_bits):
        
        self.basis, self.bits = self.initiate_bb84(n_bits, token)
        self.display_message(f"{self.client_name} Bits is: {self.bits}")

    def sender_index(self):
        if not self.O_basis:
            messagebox.showwarning(
                "Warning", 
                "The basics of the other client have not been received yet.")
        
        self.prompt_choice_bit()
        
        try:
            self.choice_index, self.check_bits, self.key = checking(
                nb_bits=self.get_n_bits(),
                alice_basis=self.basis,
                bob_basis=self.O_basis,
                bits=self.bits,
                bit_choice=self.choice_bit
            )
        except Exception as e:
            self.send("Exception", f"Error: {e}".replace("<END>", ""))
            messagebox.showerror("Erreur", str(e))
            self.restart_protocol()
            return
                
        self.display_message(f"The chosen indexes are: {self.choice_index}")
        
        self.send("INDEX", concatenate_data(self.choice_index))
        
        self.send("CHECK", concatenate_data(self.check_bits))
    
    def sender_check(self):
        try:
            self.response, self.qber, self.final_key = qber_key(
                self.check_bits, 
                self.O_check_bits, 
                self.choice_index, 
                self.key)
        except Exception as e:
            self.send("Exception", f"Error: {e}".replace("<END>", ""))
            messagebox.showerror("Error", str(e))
            self.restart_protocol()
            return
            
        self.send("RESP", f"{self.response}")
        
        #activate the button
        self.repeat_button.grid(row=1, column=3, padx=2, pady=2)
    
    def continue_sender(self):       
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"The generated key is: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"The AES key is: {self.key}")

                if self.compter >= 3 and self.O_response:
                    init_db()
                    store_key(self.client_name, self.other_name, self.key)
                    messagebox.showinfo(
                        "Info", 
                        decision(self.response))
                    self.clear_log()
                    
                    self.send_message_button.config(state='normal')
                    self.repeat_button.grid_remove()
                else:
                    text = "You must repeat this process at least "\
                        f"{3-self.compter} times to be sure of the "\
                        "integrity of the key."
                    messagebox.showinfo("Info", text)
                    self.compter += 1
                    
            else:
                messagebox.showwarning("Warning", "No final key generated.")
        else:
            self.compter = 1
            messagebox.showinfo("Info", "No valid key.Restarting the process.")

    def receiver_qam(self, n_bits):
        IBMProvider.save_account(token, overwrite=True)

        # Receive the quantum circuit
        qc_str = base64.b64decode(self.QC).decode('utf-8')
        self.qc = QuantumCircuit.from_qasm_str(qc_str)

        # Prepare basis
        self.basis, _ = self.generate_bb84_data(nb_bits=n_bits)
        self.send("BASIS", concatenate_data(self.basis))
    

        # Measure the qubits
        self.qc = bob_measure(self.qc, self.basis)
        try:
            self.bits = calcul(self.qc, self.backend)
        except Exception as e:
            self.send("Exception", f"Error: {e}".replace("<END>", ""))
            messagebox.showerror("Error", str(e))
            self.backend = ""
            self.prompt_backend()
            self.restart_protocol()
            return
        self.display_message(f"{self.client_name} Bits is: {self.bits}")

    def receiver_basis(self):
        self.display_message(f"{self.client_name} Basis is: {self.basis}")
        self.display_message(f"{self.other_name} Basis is: {self.O_basis}")

    def receiver_index(self):
        
        try:
            _, self.check_bits, self.key = checking(
                nb_bits=self.get_n_bits(),
                alice_basis=self.O_basis,
                bob_basis=self.basis,
                bits=self.bits,
                bit_choice=self.choice_bit,
                choice_index=self.O_index
            )
            
        except Exception as e:
            self.send("Exception", f"Error: {e}".replace("<END>", ""))
            messagebox.showerror("Error", str(e))
            return
            
        self.send("CHECK", concatenate_data(self.check_bits))


    def receiver_check(self):
        try:
            self.response, self.qber, self.final_key = qber_key(
                self.O_check_bits, 
                self.check_bits, 
                self.O_index, 
                self.key)
        except Exception as e:
            self.send("Exception", f"Error: {e}".replace("<END>", ""))
            messagebox.showerror("Error", str(e))
            return

        self.send("RESP", f"{self.response}")

    def continue_receiver(self):
        if self.response:
            self.display_message(f"QBER: {self.qber}")
            self.display_message(f"The generated key is: {self.final_key}")
            if self.final_key:
                self.key = key_from_bits(self.final_key)
                self.display_message(f"The AES key is: {self.key}")

                if self.compter >= 3 and self.O_response:
                    init_db()
                    store_key(self.other_name, self.client_name, self.key)
                    messagebox.showinfo(
                        "Info", 
                        decision(self.response))
                    self.clear_log()
                    
                    self.send_message_button.config(state='normal')
                else:
                    text = "You must repeat this process at least "\
                        f"{3-self.compter} times to be sure of the "\
                        "integrity of the key."
                    messagebox.showinfo("Info", text)
                    self.compter += 1

            else:
                messagebox.showwarning("Warning", "No final key generated.")
        else:
            self.compter = 1
            messagebox.showinfo("Info", 
                                "No valid key. Restarting the process.")

    def initiate_bb84(self, nb_bits, token):
        self.display_message(
            f"{self.client_name} has initiated BB84 Protocol.")
        
        basis, bits = self.generate_bb84_data(nb_bits)
        qc = prepare_qubits(bits, basis, token)
        qc_str = dumps(qc)
        qasm_circuit = base64.b64encode(qc_str.encode()).decode('utf-8')

        self.send("QC", qasm_circuit)
    
        self.send("BASIS", concatenate_data(basis))
    
        return basis, bits

    def generate_bb84_data(self, nb_bits=default_n_bits):
        basis = np.random.randint(2, size=nb_bits).tolist()
        bits = np.random.randint(2, size=nb_bits).tolist()
        return basis, bits

    def send_message(self):
        message_content = self.message_entry.get()
        if message_content and self.key and self.sock:
            encrypted_message = encrypt_aes(message_content, self.key)
            self.send("MESSAGE", f"{encrypted_message}")
            self.display_message(f"You: {message_content}")
            self.message_entry.delete(0, tk.END)

    def send(self, action, content):
        message = f"{action}:{content}<END>"
        try:
            if self.sock:
                self.sock.sendall(message.encode())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            if self.sock:
                self.sock.close()

    def on_closing(self):
        if not messagebox.askokcancel("Quit", "Do you want to quit?"):
            return
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except OSError as e:
                messagebox.showerror("Error", f"Failed to close socket: {e}")
                
        self.quit()
        self.after(100, self.destroy)
            

    def disconnect(self):
        if not self.sock:
            return
        self.running = False
        self.compter = 1
        self.display_attempt(self.compter)
        
        try:
            self.send(
                'DISCONNECT', 
                f"{self.client_name} has disconnected".replace("<END>", ""))
        except Exception as e:
            messagebox.showerror("Error", 
                                f"Failed to send disconnect message: {e}")


        self.connect_button.config(state='normal')
        self.disconnect_button.config(state='disabled')
        self.send_message_button.config(state='disabled')
        self.sock = None
            
    

if __name__ == "__main__":
    app = QuantumChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
