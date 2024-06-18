import socket
import time
import random
from packet import Packet, PACKET_SIZE, DATA_SIZE, MESSAGE_TYPE_DATA, MESSAGE_TYPE_ACK, MESSAGE_TYPE_FIN, MESSAGE_TYPE_SYN, MESSAGE_TYPE_SYN_ACK

# Constantes de configuração
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
CLIENT_PORT = 54321
TIMEOUT = 2  # Timeout em segundos
MAX_RETRIES = 5  # Número máximo de tentativas de retransmissão
LOSS_PROBABILITY = 0.1  # Probabilidade de perda ou corrompimento de pacotes (para simulação de erros)

# Estados do congestionamento
SLOW_START = 0
CONGESTION_AVOIDANCE = 1

# Tamanho da janela de congestionamento inicial e limite
INITIAL_CWND = 1
CWND_LIMIT = 16

def client(file_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", CLIENT_PORT))
    sock.settimeout(TIMEOUT)

    # Estabelecimento da conexão (three-way handshake)
    syn_packet = Packet(MESSAGE_TYPE_SYN, 0)
    sock.sendto(syn_packet.to_bytes(), (SERVER_IP, SERVER_PORT))
    print("Sent SYN")

    while True:
        try:
            syn_ack_packet, _ = sock.recvfrom(PACKET_SIZE)
            syn_ack = Packet.from_bytes(syn_ack_packet)
            if syn_ack.message_type == MESSAGE_TYPE_SYN_ACK:
                print("Received SYN-ACK")
                ack_packet = Packet(MESSAGE_TYPE_ACK, 1)
                sock.sendto(ack_packet.to_bytes(), (SERVER_IP, SERVER_PORT))
                print("Sent ACK, connection established")
                break
        except socket.timeout:
            print("Timeout, resending SYN")
            sock.sendto(syn_packet.to_bytes(), (SERVER_IP, SERVER_PORT))

    with open(file_path, "rb") as file:
        file_data = file.read()

    total_packets = (len(file_data) + DATA_SIZE - 1) // DATA_SIZE
    base = 0
    next_seq_num = 0
    cwnd = INITIAL_CWND
    state = SLOW_START

    while base < total_packets:
        window_packets = []

        # Envio dos pacotes dentro da janela de congestionamento
        while next_seq_num < base + cwnd and next_seq_num < total_packets:
            start = next_seq_num * DATA_SIZE
            end = start + DATA_SIZE
            data = file_data[start:end]
            packet = Packet(MESSAGE_TYPE_DATA, next_seq_num, data)

            if random.random() >= LOSS_PROBABILITY:
                sock.sendto(packet.to_bytes(), (SERVER_IP, SERVER_PORT))
                print(f"Sent packet {next_seq_num}")
            else:
                print(f"Simulating loss or corruption for packet {next_seq_num}")
                if random.random() >= 0.5:
                    print(f"Lost packet {next_seq_num}")
                    continue
                else:
                    # Simula corrupção de pacote
                    packet.data = b'\0' * DATA_SIZE
                    sock.sendto(packet.to_bytes(), (SERVER_IP, SERVER_PORT))
                    print(f"Sent corrupted packet {next_seq_num}")

            window_packets.append(packet)
            next_seq_num += 1

        # Recepção de ACKs e controle de congestionamento
        try:
            while base < next_seq_num:
                ack_packet, _ = sock.recvfrom(PACKET_SIZE)
                ack = Packet.from_bytes(ack_packet)
                if ack.message_type == MESSAGE_TYPE_ACK:
                    ack_num = ack.seq_num
                    print(f"Received ACK {ack_num}")

                    if ack_num >= base:
                        base = ack_num + 1
                        if state == SLOW_START:
                            cwnd *= 2
                            if cwnd >= CWND_LIMIT:
                                state = CONGESTION_AVOIDANCE
                                cwnd = CWND_LIMIT
                        elif state == CONGESTION_AVOIDANCE:
                            cwnd += 1

        except socket.timeout:
            # Timeout: retransmite todos os pacotes da janela
            print("Timeout, retransmitting packets")
            next_seq_num = base
            cwnd = INITIAL_CWND
            state = SLOW_START

    # Envio do pacote de encerramento da conexão
    fin_packet = Packet(MESSAGE_TYPE_FIN, 0)
    sock.sendto(fin_packet.to_bytes(), (SERVER_IP, SERVER_PORT))
    print("Connection closed")
    sock.close()