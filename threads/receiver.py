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
        # TODO: check if the port below is correct
        data, address = self.socket.recvfrom(1024)

        if data:
            print("Received ACK", data.decode())
            seq_number = data.decode()[:self.seq_dig]
            checksum = data.decode()[self.seq_dig:]

            text_chunk = self.window[int(seq_number) - 1]
            if checksum == checksum_of(text_chunk):
                self.window.ack(seq_number)

        # TODO: compute timeout

    def run(self):
        running = True
        self.socket.bind(('0.0.0.0', self.port))

        # TODO: change timeout according to formula
        self.socket.settimeout(90)
        while running:
            self.__receive_ack()
            time.sleep(0.1)
