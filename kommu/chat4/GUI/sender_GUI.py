import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading
import socket

def decode_message(data):
    return data.split(':', 1)

class QuantumChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Client")
        self.geometry("500x400")

        self.client_data = {}
        self.setup_ui()
        self.sock = None

    def setup_ui(self):
        # UI Components for connection
        self.host_label = tk.Label(self, text="Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.host_entry = tk.Entry(self, width=15)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_label = tk.Label(self, text="Port:")
        self.port_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.port_entry = tk.Entry(self, width=5)
        self.port_entry.insert(0, '6555')
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=10, pady=10)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.prompt_user_name()
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.sock = None

    def prompt_user_name(self):
        while True:
            self.client_name = simpledialog.askstring("Name", "Enter your name:", parent=self)
            if self.client_name:
                self.send("REGISTER", self.client_name)
                break

    def prompt_partner_name(self):
        while True:
            partner_name = simpledialog.askstring("Partner", "Enter the name of the client you wish to connect to:", parent=self)
            if partner_name:
                self.send("CONNECT", partner_name)
                break

    def send(self, action, content):
        message = f"{action}:{content}".encode()
        if self.sock:
            try:
                self.sock.sendall(message)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")
                self.sock.close()
                self.sock = None

    def receive_messages(self):
        while self.sock:
            try:
                data = self.sock.recv(4096).decode()
                if data:
                    action, content = decode_message(data)
                    self.process_server_message(action, content)
                else:
                    break
            except Exception as e:
                messagebox.showerror("Error", f"Error receiving data: {e}")
                break
        self.sock.close()

    def process_server_message(self, action, content):
        if action == "ERROR" and "Name already in use" in content:
            messagebox.showerror("Error", content)
            self.prompt_user_name()
        elif action == "REGISTER":
            messagebox.showinfo("Registered", "You are registered successfully.")
            self.connect_button['state'] = 'disabled'
            self.prompt_partner_name()
        elif action == "CONNECT":
            if "not available" in content or "cannot communicate with yourself" in content:
                messagebox.showerror("Connection Error", content)
                self.prompt_partner_name()
            else:
                messagebox.showinfo("Connection Established", f"Connected with {content.split(':')[0]}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.sock:
                self.sock.close()
            self.destroy()

if __name__ == "__main__":
    app = QuantumChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
