import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading
import json
import random
import textwrap

GRID_SIZE = 5
FREE_SPACE = "FREE"
BUFFER_SIZE = 1024
DEFAULT_PORT = 5000

# Networking Utilities
def send_message(sock, data):
    """Send a JSON-encoded message over a socket."""
    message = json.dumps(data).encode('utf-8')
    sock.sendall(message)


def receive_message(sock):
    """Receive a JSON-encoded message over a socket."""
    data = b""
    while True:
        part = sock.recv(BUFFER_SIZE)
        if not part:
            break
        data += part
    return json.loads(data.decode('utf-8'))


# Host a Game
class BingoHost:
    def __init__(self, title, items, port=DEFAULT_PORT):
        self.title = title
        self.items = items
        self.port = port
        self.clients = []

    def start_server(self):
        """Start the Bingo host server."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        server.listen(5)
        threading.Thread(target=self.accept_clients, args=(server,), daemon=True).start()
        print(f"Hosting Bingo game '{self.title}' on port {self.port}...")

    def accept_clients(self, server):
        """Accept incoming client connections."""
        while True:
            client, address = server.accept()
            print(f"Client connected from {address}")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        """Handle communication with a client."""
        try:
            send_message(client, {"title": self.title, "items": self.items})
            request = receive_message(client)
            if request.get("action") == "get_card":
                card = self.create_bingo_card()
                send_message(client, {"card": card})
        except (socket.error, json.JSONDecodeError):
            print("Client disconnected.")
        finally:
            client.close()

    def create_bingo_card(self):
        """Create a randomized Bingo card for the client."""
        return random.sample(self.items, GRID_SIZE**2 - 1)


# Join a Game
class BingoClient:
    def __init__(self, host, port=DEFAULT_PORT):
        self.host = host
        self.port = port

    def connect_to_host(self):
        """Connect to the Bingo host."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))
        game_data = receive_message(client)
        send_message(client, {"action": "get_card"})
        response = receive_message(client)
        return game_data, response["card"]


# GUI Components
def host_game_gui():
    """GUI for hosting a Bingo game."""
    setup_window = tk.Tk()
    setup_window.title("Host a Game")

    tk.Label(setup_window, text="Game Title:", font=("Arial", 14)).pack(pady=5)
    title_entry = tk.Entry(setup_window, font=("Arial", 14), width=30)
    title_entry.pack(pady=5)

    tk.Label(setup_window, text="Bingo Items (one per line):", font=("Arial", 14)).pack(pady=5)
    items_text = tk.Text(setup_window, font=("Arial", 12), width=30, height=10)
    items_text.pack(pady=5)

    def start_hosting():
        title = title_entry.get().strip()
        items = items_text.get("1.0", tk.END).strip().splitlines()
        if not title or len(items) < GRID_SIZE**2 - 1:
            messagebox.showerror("Error", "Please provide a title and at least 24 items.")
            return
        setup_window.destroy()

        # Start hosting
        host = BingoHost(title, items)
        host.start_server()

        # Show the host's Bingo card
        host_card = host.create_bingo_card()
        show_bingo_card(title, host_card)

        # Notify host of successful hosting
        messagebox.showinfo("Hosting", f"Hosting game '{title}'. Share your IP with others.")

    tk.Button(setup_window, text="Start Hosting", font=("Arial", 14), command=start_hosting).pack(pady=10)

    setup_window.mainloop()


def join_game_gui():
    """GUI for joining a Bingo game."""
    join_window = tk.Tk()
    join_window.title("Join a Game")

    tk.Label(join_window, text="Enter Host IP Address:", font=("Arial", 14)).pack(pady=5)
    ip_entry = tk.Entry(join_window, font=("Arial", 14), width=30)
    ip_entry.pack(pady=5)

    def connect_to_host():
        host_ip = ip_entry.get().strip()
        if not host_ip:
            messagebox.showerror("Error", "Please enter a valid IP address.")
            return
        try:
            client = BingoClient(host_ip)
            game_data, card = client.connect_to_host()
            messagebox.showinfo("Connected", f"Joined game: {game_data['title']}")
            show_bingo_card(game_data['title'], card)
        except (socket.error, json.JSONDecodeError):
            messagebox.showerror("Error", "Failed to connect to host.")
            return

    tk.Button(join_window, text="Join Game", font=("Arial", 14), command=connect_to_host).pack(pady=10)

    join_window.mainloop()


def show_bingo_card(title, card):
    """Display the Bingo card."""
    card_window = tk.Tk()
    card_window.title(title)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            item = FREE_SPACE if i == GRID_SIZE // 2 and j == GRID_SIZE // 2 else card.pop(0)
            tk.Label(card_window, text=item, font=("Arial", 12), width=10, height=2, relief="solid").grid(row=i, column=j, padx=5, pady=5)

    card_window.mainloop()


def main_menu():
    """Main menu GUI."""
    root = tk.Tk()
    root.title("Bingo Game")

    tk.Label(root, text="Welcome to Bingo!", font=("Arial", 24)).pack(pady=20)

    tk.Button(root, text="Host a Game", font=("Arial", 16), command=lambda: (root.destroy(), host_game_gui())).pack(pady=10)
    tk.Button(root, text="Join a Game", font=("Arial", 16), command=lambda: (root.destroy(), join_game_gui())).pack(pady=10)

    root.mainloop()


# Run the Application
main_menu()
