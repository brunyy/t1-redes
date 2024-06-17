import socket
import zlib
import random
import time
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
CLIENT_PORT = 54321
# Estados do congestionamento
SLOW_START = 0
CONGESTION_AVOIDANCE = 1
INITIAL_CWND = 1
CWND_LIMIT = 16

MAX_RETRIES = 5   # Número máximo de tentativas de retransmissão
LOSS_PROBABILITY = 0.1  # Probabilidade de perda de pacotes (para simulação de erros)

TIMEOUT = 2       # Timeout em segundos

PACKET_SIZE = 10  # Tamanho do pacote em bytes

def calculate_crc(data):
    return zlib.crc32(data)

def create_packet(seq_num, data):
    crc = calculate_crc(data)
    header = struct.pack('!I I', seq_num, crc)
    return header + data

def client(file_path):
    # Estabelecimento da conexão
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", CLIENT_PORT))
    sock.settimeout(TIMEOUT)

    with open(file_path, "rb") as file:
        file_data = file.read()

    total_packets = (len(file_data) + PACKET_SIZE - 1) // PACKET_SIZE
    base = 0
    next_seq_num = 0
    cwnd = INITIAL_CWND
    state = SLOW_START

    while base < total_packets:
        window_packets = []

        # Envio dos pacotes dentro da janela de congestionamento
        while next_seq_num < base + cwnd and next_seq_num < total_packets:
            start = next_seq_num * PACKET_SIZE
            end = start + PACKET_SIZE
            data = file_data[start:end].ljust(PACKET_SIZE, b'\0')
            packet = create_packet(next_seq_num, data)

            if random.random() >= LOSS_PROBABILITY:
                sock.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f"Sent packet {next_seq_num}")
            else:
                print(f"Simulating loss for packet {next_seq_num}")

            window_packets.append(packet)
            next_seq_num += 1

        # Recepção de ACKs e controle de congestionamento
        try:
            while base < next_seq_num:
                ack_packet, _ = sock.recvfrom(8)
                ack_num, _ = struct.unpack('!I I', ack_packet)
                print(f"Received ACK {ack_num}")

                if ack_num > base:
                    base = ack_num
                    if state == SLOW_START:
                        cwnd *= 2
                        if cwnd >= CWND_LIMIT:
                            state = CONGESTION_AVOIDANCE
                            cwnd = CWND_LIMIT
                    elif state == CONGESTION_AVOIDANCE:
                        cwnd += 1

        except socket.timeout:
            # Timeout: retransmit all packets in the window
            print("Timeout, retransmitting packets")
            next_seq_num = base
            cwnd = INITIAL_CWND
            state = SLOW_START

    # Envio do pacote de encerramento da conexão
    sock.sendto(b'FIN', (SERVER_IP, SERVER_PORT))
    print("Connection closed")
    sock.close()