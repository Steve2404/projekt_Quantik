import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import socket
import threading
import base64
from function import send, receive, decode_message, name_ask
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Variables de configuration
HOST = 'localhost'
PORT = 6555

class ChatApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Client")
        self.geometry("400x500")

        self.init_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.sock = None
        self.running = True
        self.client_name = None

    def init_widgets(self):
        # Host and Port configuration
        self.host_entry = tk.Entry(self, width=30)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.pack(pady=10)

        self.port_entry = tk.Entry(self, width=30)
        self.port_entry.insert(0, '6555')
        self.port_entry.pack(pady=10)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=10)

        # Message area
        self.message_area = scrolledtext.ScrolledText(self, state='disabled', width=40, height=10)
        self.message_area.pack(pady=10)

        # Message entry
        self.message_entry = tk.Entry(self, width=30)
        self.message_entry.pack(pady=10)

        self.send_button = tk.Button(self, text="Send Message", command=self.send_message)
        self.send_button.pack(pady=10)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.append_message("Connected to the server.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def send_message(self):
        message = self.message_entry.get()
        if message:
            send(self.sock, "MESSAGE", message)
            self.append_message(f"You: {message}")
            self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while self.running:
            try:
                message = receive(self.sock)
                self.append_message(message)
            except Exception as e:
                self.append_message(f"Error: {str(e)}")
                break

    def append_message(self, message):
        self.message_area.config(state='normal')
        self.message_area.insert(tk.END, message + '\n')
        self.message_area.yview(tk.END)
        self.message_area.config(state='disabled')

    def on_closing(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.destroy()

if __name__ == "__main__":
    app = ChatApplication()
    app.mainloop()
