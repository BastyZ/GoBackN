from objects.checksum import calculate_checksum as checksum_of

import threading
import time
import socket


class Receiver(threading.Thread):
    def __init__(self, window, port, seq_digits, lock, name):
        threading.Thread.__init__(self, name=name)
        self.window = window
        self.port = port
        self.seq_dig = seq_digits
        self.lock = lock
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.0)

    def __receive_ack(self):
        data, address = self.socket.recvfrom(1024)      # Buffer size

        if data:
            seq_number = data.decode()[:self.seq_dig]
            checksum = data.decode()[self.seq_dig:]

            self.window.ack(seq_number, checksum)

    def run(self):
        self.socket.bind(('0.0.0.0', self.port))

        self.socket.settimeout(90)
        while not self.window.has_finished():
            self.__receive_ack()
            time.sleep(0.1)
        print("ReceiverThread :: Stopped waiting for ACKs")
        return 0
