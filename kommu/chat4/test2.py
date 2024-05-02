import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        # Layout configuration
        master.geometry("400x300")

        # Host and port entry
        tk.Label(master, text="Host:").pack()
        self.host_entry = tk.Entry(master)
        self.host_entry.pack()

        tk.Label(master, text="Port:").pack()
        self.port_entry = tk.Entry(master)
        self.port_entry.pack()

        # Connect button
        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()

        # Message display (ScrolledText widget)
        self.message_area = scrolledtext.ScrolledText(master)
        self.message_area.pack(pady=5)

        # Message entry
        tk.Label(master, text="Enter your message:").pack()
        self.message_entry = tk.Entry(master)
        self.message_entry.pack()

        # Send button
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.message_area.insert(tk.END, "Connected to the server.\n")

    def send_message(self):
        message = self.message_entry.get()
        self.sock.sendall(message.encode())
        self.message_area.insert(tk.END, f"You: {message}\n")
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    self.message_area.insert(tk.END, f"Received: {data.decode()}\n")
            except ConnectionError:
                break

if __name__ == "__main__":
    root = tk.Tk()
    chat_client = ChatClient(root)
    root.mainloop()
