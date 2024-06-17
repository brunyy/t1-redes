import socket
import zlib

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

def calculate_crc(data):
    return zlib.crc32(data)

def is_packet_corrupted(packet):
    seq_num, crc, data = parse_packet(packet)
    return crc != calculate_crc(data)

def parse_packet(packet):
    header = packet[:8]
    data = packet[8:]
    seq_num, crc = struct.unpack('!I I', header)
    return seq_num, crc, data    

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))

    expected_seq_num = 0
    received_data = b""

    while True:
        packet, addr = sock.recvfrom(1024)

        if packet == b'FIN':
            print("Received FIN, closing connection")
            break

        if is_packet_corrupted(packet):
            print("Corrupted packet received, discarding")
            continue

        seq_num, _, data = parse_packet(packet)
        if seq_num == expected_seq_num:
            received_data += data.rstrip(b'\0')
            expected_seq_num += 1

        ack_packet = struct.pack('!I I', expected_seq_num, 0)
        sock.sendto(ack_packet, addr)
        print(f"Sent ACK {expected_seq_num}")

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

if __name__ == "__main__":
    import sys
    from threading import Thread

    if len(sys.argv) != 3:
        print("Usage: python transfer.py <client/server> <file_path>")
        sys.exit(1)

    role = sys.argv[1]
    file_path = sys.argv[2]

    if role == "client":
        client(file_path)
    elif role == "server":
        server()
    else:
        print("Invalid role. Choose 'client' or 'server'.")