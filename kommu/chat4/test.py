import tkinter as tk
import socket
import threading

class SocketSimulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Socket Simulator")

        self.host_label = tk.Label(master, text="Host:")
        self.host_label.grid(row=0, column=0)

        self.host_entry = tk.Entry(master)
        self.host_entry.grid(row=0, column=1)

        self.port_label = tk.Label(master, text="Port:")
        self.port_label.grid(row=1, column=0)

        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=1, column=1)

        self.name_label = tk.Label(master, text="Your Name:")
        self.name_label.grid(row=2, column=0)

        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=2, column=1)

        self.message_label = tk.Label(master, text="Messages:")
        self.message_label.grid(row=3, column=0, sticky=tk.W)

        self.message_text = tk.Text(master, width=40, height=10)
        self.message_text.grid(row=4, column=0, columnspan=2)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.grid(row=5, column=0, columnspan=2)

    def send_message(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        name = self.name_entry.get()
        message = self.message_text.get("1.0", tk.END)

        # Code for sending message via socket goes here
        # This is just a placeholder

        print("Host:", host)
        print("Port:", port)
        print("Name:", name)
        print("Message:", message)

root = tk.Tk()
app = SocketSimulatorGUI(root)
root.mainloop()
