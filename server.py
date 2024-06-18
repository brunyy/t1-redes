import socket
import os
import hashlib
from packet import Packet, PACKET_SIZE, MESSAGE_TYPE_ACK, MESSAGE_TYPE_FIN, MESSAGE_TYPE_SYN, MESSAGE_TYPE_SYN_ACK

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
CLIENT_PORT = 54321

def server(file_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))

    expected_seq_num = 0
    received_data = b""

    while True:
        packet_bytes, addr = sock.recvfrom(PACKET_SIZE)
        packet = Packet.from_bytes(packet_bytes)

        if packet.message_type == MESSAGE_TYPE_SYN:
            print("Received SYN")
            syn_ack_packet = Packet(MESSAGE_TYPE_SYN_ACK, 0)
            sock.sendto(syn_ack_packet.to_bytes(), addr)
            print("Sent SYN-ACK")
            continue

        if packet.message_type == MESSAGE_TYPE_ACK and packet.seq_num == 1:
            print("Received ACK, connection established")
            break

    while True:
        packet_bytes, addr = sock.recvfrom(PACKET_SIZE)
        packet = Packet.from_bytes(packet_bytes)

        if packet.message_type == MESSAGE_TYPE_FIN:
            print("Received FIN, closing connection")
            break

        if packet.is_corrupted():
            print("Corrupted packet received, discarding")
            continue

        if packet.seq_num == expected_seq_num:
            received_data += packet.data.rstrip(b'\0')
            expected_seq_num += 1

        ack_packet = Packet(MESSAGE_TYPE_ACK, expected_seq_num - 1)
        sock.sendto(ack_packet.to_bytes(), addr)
        print(f"Sent ACK {expected_seq_num - 1}")

    with open("received_file", "wb") as file:
        file.write(received_data)

    sock.close()

    # Verificação do arquivo recebido
    print("Verifying file integrity...")
    with open("received_file", "rb") as f:
        received_hash = hashlib.md5(f.read()).hexdigest()
    with open(file_path, "rb") as f:
        original_hash = hashlib.md5(f.read()).hexdigest()

    if received_hash == original_hash:
        print("File received correctly")
    else:
        print("File corrupted during transfer")