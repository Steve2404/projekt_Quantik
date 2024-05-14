import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import threading
import socket
import time

def decode_message(data):
    """Decode incoming messages; assuming format 'action:content'."""
    return data.split(':', 1)

class QuantumChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Chat Client")
        self.geometry("600x400")

        self.client_data = {}
        self.setup_ui()
        self.sock = None
        self.client_name = None
        self.running = True
        self.data_lock = threading.Lock()

    def setup_ui(self):
        # UI Components
        self.host_label = tk.Label(self, text="Host:")
        self.host_entry = tk.Entry(self, width=15)
        self.host_entry.insert(0, 'localhost')
        
        self.port_label = tk.Label(self, text="Port:")
        self.port_entry = tk.Entry(self, width=5)
        self.port_entry.insert(0, '6555')
        
        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server)
        
        self.messages_area = scrolledtext.ScrolledText(self, state='disabled', height=15)
        self.message_entry = tk.Entry(self, width=40)
        self.send_button = tk.Button(self, text="Send", command=self.send_message)

        # Grid layout
        self.host_label.grid(row=0, column=0)
        self.host_entry.grid(row=0, column=1)
        self.port_label.grid(row=0, column=2)
        self.port_entry.grid(row=0, column=3)
        self.connect_button.grid(row=0, column=4)
        self.messages_area.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=(5,0))
        self.message_entry.grid(row=2, column=0, columnspan=4, pady=5)
        self.send_button.grid(row=2, column=4)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.client_name = simpledialog.askstring("Name", "Enter your name:", parent=self)
        if not self.client_name:
            messagebox.showinfo("Info", "No name entered. Connection cancelled.")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.send("REGISTER", self.client_name)
            
            while True:
                time.sleep(2)  
                with self.data_lock:
                    if self.client_data[self.client_name]['ack'] is not None:
                        self.update_chat_window('ack', self.client_data[self.client_name]['ack'])
                        break
                    elif self.client_data[self.client_name]['error'] is not None:
                        messagebox.showerror("Error", f"Error >> {self.client_data[self.client_name]['error']}")
                        messagebox.showinfo("Info", "Change your name .....")
                        self.client_name = simpledialog.askstring("Name", "Enter your name:", parent=self)
                        self.send("REGISTER", self.client_name)
            
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            self.sock = None

    def send_message(self):
        if message := self.message_entry.get():
            self.send("MESSAGE", message)
            self.message_entry.delete(0, tk.END)

    def send(self, action, content):
        message = f"{action}:{content}".encode()
        if self.sock:
            try:
                self.sock.sendall(message)
            except Exception as e:
                self.messages_area.insert(tk.END, f"Failed to send message: {e}\n")
                self.sock.close()
                self.sock = None

    def receive_messages(self):
        while self.running and self.sock:
            try:
                if data := self.sock.recv(4096).decode():
                    action, content = decode_message(data)
                    self.update_chat_window(action, content)
                    self.process_action(action, content)
                else:
                    break
            except Exception as e:
                self.update_chat_window("Error", f"Error receiving data: {e}")
                break
        self.sock.close()
        self.sock = None

    def process_action(self, action, content):
        if action in ["MESSAGE", "ACK", "ERROR", "RESP", "ROLE", "BASIS", "QC"]:
            if action == "REGISTER":
                client_name = content.split(":>")[0]
                if client_name not in self.client_data:
                    self.client_data[client_name] = {
                        "basis":      None,
                        "bit":        None,
                        "QC":         None,
                        "index":      None,
                        "check_bits": None,
                        "resp":       None,
                        "decis":      None,
                        "msg":        None,
                        "other":      None,
                        "error2":     None,
                        "error":      None,
                        "ack":        content,
                        "ack2":       None,
                        "role":       None,
                        "disc":       None
                    }
            elif action == "MESSAGE":
                message = content.split(":>")[1]
                if client_name:
                    self.client_data[client_name]["msg"] = message
            elif action == "ERROR":
                        client_name, content = content.split(":>")
                        self.client_data[client_name]["error"] = content
            else:        
                self.client_data[action] = content  # Store data based on action
            #self.update_chat_window(action, f"Processed {action}: {content}")

    def update_chat_window(self, action, message):
        self.messages_area.config(state='normal')
        self.messages_area.insert(tk.END, f"{action}: {message}\n")
        self.messages_area.yview(tk.END)
        self.messages_area.config(state='disabled')

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.running = False
            if self.sock:
                self.sock.close()
            self.destroy()

if __name__ == "__main__":
    app = QuantumChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
