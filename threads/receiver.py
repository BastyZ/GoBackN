from objects.checksum import calculate_checksum as checksum_of

import threading
import time
import socket


class Receiver(threading.Thread):
    def __init__(self, window, port, seq_digits):
        threading.Thread.__init__(self)
        self.window = window
        self.port = port
        self.seq_dig = seq_digits
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __receive_ack(self):
        data, address = self.socket.recvfrom(1024)      # Buffer size

        if data:
            print("Received ACK", data.decode())
            seq_number = data.decode()[:self.seq_dig]
            checksum = data.decode()[self.seq_dig:]

            self.window.ack(seq_number, checksum)

    def run(self):
        running = True
        self.socket.bind(('0.0.0.0', self.port))

        self.socket.settimeout(90)
        while running:
            self.__receive_ack()
            time.sleep(0.1)
