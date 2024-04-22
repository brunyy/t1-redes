import socket
import threading

class ChatServer:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()

    def handle_client(self, client_socket, client_address):
        print(f"Connection from {client_address} established.")

        try:
            username = None

            while True:
                message = client_socket.recv(1024).decode("utf-8")

                if not message:
                    break

                if message.startswith("/reg"):
                    parts = message.split(" ", 1)
                    if len(parts) == 2:
                        username = parts[1]
                        self.clients[username] = client_socket
                        print(f"{username} registered.")
                    else:
                        client_socket.send("Invalid /reg command. Usage: /reg username".encode("utf-8"))
                elif message.startswith("/msg"):
                    if username:
                        parts = message.split(" ", 2)
                        if len(parts) == 3:
                            to_user = parts[1]
                            content = parts[2]
                            if to_user in self.clients:
                                self.clients[to_user].send(f"{username}: {content}".encode("utf-8"))
                            else:
                                client_socket.send(f"User '{to_user}' not found.".encode("utf-8"))
                        else:
                            client_socket.send("Invalid /msg command. Usage: /msg \"to_user\" content".encode("utf-8"))
                    else:
                        client_socket.send("You need to register first.".encode("utf-8"))
                elif message.startswith("/file"):
                    client_socket.send("File transfer is not supported in this version.".encode("utf-8"))
                elif message == "/quit":
                    break
                else:
                    client_socket.send("Invalid command.".encode("utf-8"))

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            if username:
                del self.clients[username]
            client_socket.close()
            print(f"Connection from {client_address} closed.")

    def start(self):
        SERVER_IP = "0.0.0.0"
        SERVER_PORT = 12345

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(5)
        print(f"Server started listening on {SERVER_IP}:{SERVER_PORT}.")

        try:
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
            server_socket.close()

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.start()