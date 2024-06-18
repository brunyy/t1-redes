import struct
import random

PACKET_SIZE = 10
DATA_SIZE = 6  # Tamanho dos dados em bytes (bytes 5 a 10), restante é o cabeçalho

# Definição dos tipos de mensagem
MESSAGE_TYPE_DATA = 0x01
MESSAGE_TYPE_ACK = 0x02
MESSAGE_TYPE_FIN = 0x03
MESSAGE_TYPE_SYN = 0x04
MESSAGE_TYPE_SYN_ACK = 0x05

class Packet:
    def __init__(self, message_type, seq_num, data=b''):
        self.message_type = message_type
        self.seq_num = seq_num
        # Padding
        self.data = data.ljust(DATA_SIZE, b'\0')[:DATA_SIZE]
        self.crc = self.calculate_crc()

    def calculate_crc(self):
        crc_data = struct.pack('!B H', self.message_type, self.seq_num) + self.data
        crc = 0
        for byte in crc_data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    def to_bytes(self):
        # 1 byte para o tipo da mensagem, 2 para o seq_num e 1 para o crc8
        header = struct.pack('!B H B', self.message_type, self.seq_num, self.crc)
        print(f'header: {len(header)}')
        print(f'data: {len(self.data)}')
        # 4 bytes de header e 6 de dados, totalizando 10
        return header + self.data

    @staticmethod
    def from_bytes(packet_bytes):
        header = packet_bytes[:4]
        data = packet_bytes[4:]
        message_type, seq_num, crc = struct.unpack('!B H B', header)
        packet = Packet(message_type, seq_num, data)
        packet.crc = crc
        return packet

    def is_corrupted(self):
        return self.crc != self.calculate_crc()