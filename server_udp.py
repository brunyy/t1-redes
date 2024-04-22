import socket
import threading

class UdpServer:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()

    def handle_client(self, client_socket, client_address):
        print(f"Connection from {client_address} established.")

        try:
            username = None

            while True:
                message, _ = client_socket.recvfrom(1024)
                message = message.decode("utf-8")

                if message.startswith("/reg"):
                    parts = message.split(" ", 1)
                    if len(parts) == 2:
                        username = parts[1]
                        self.clients[username] = client_address
                        print(f"{username} registered.")
                    else:
                        client_socket.sendto("Invalid /reg command. Usage: /reg username".encode("utf-8"), client_address)
                elif message.startswith("/msg"):
                    if username:
                        parts = message.split(" ", 2)
                        if len(parts) == 3:
                            to_user = parts[1]
                            content = parts[2]
                            if to_user in self.clients:
                                to_address = self.clients[to_user]
                                client_socket.sendto(f"{username}: {content}".encode("utf-8"), to_address)
                            else:
                                client_socket.sendto(f"User '{to_user}' not found.".encode("utf-8"), client_address)
                        else:
                            client_socket.sendto("Invalid /msg command. Usage: /msg \"to_user\" content".encode("utf-8"), client_address)
                    else:
                        client_socket.sendto("You need to register first.".encode("utf-8"), client_address)
                elif message.startswith("/file"):
                    client_socket.sendto("File transfer is not supported in this version.".encode("utf-8"), client_address)
                elif message == "/quit":
                    break
                else:
                    client_socket.sendto("Invalid command.".encode("utf-8"), client_address)

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

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        print(f"Server started listening on {SERVER_IP}:{SERVER_PORT}.")

        try:
            while True:
                client_data, client_address = server_socket.recvfrom(1024)
                client_thread = threading.Thread(target=self.handle_client, args=(server_socket, client_address))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
            server_socket.close()

if __name__ == "__main__":
    udp_server = UdpServer()
    udp_server.start()