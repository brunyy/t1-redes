import socket
import os
import hashlib

from client import client
from server import server

if __name__ == "__main__":
    import sys
    from threading import Thread

    if len(sys.argv) != 3:
        print("Usage: python main.py <client/server> <file_path>")
        sys.exit(1)

    role = sys.argv[1]
    file_path = sys.argv[2]

    if role == "client":
        client(file_path)
    elif role == "server":
        server(file_path)
    else:
        print("Invalid role. Choose 'client' or 'server'.")