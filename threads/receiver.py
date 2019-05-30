from objects.checksum import calculate_checksum

import threading
import time
import socket


class Receiver(threading.Thread):
    def __init__(self, window, port, seq_digits, lock, name):
        """
        Subclass of threading.Thread, implements the receiver thread of Go Back N algorithm.
        :param window: Window used in Go Back N algorithm
        :param port: Port used by this thread to receive ACKs
        :param seq_digits: Sequence number length on bytes
        :param lock: Lock used to avoid data races when using the window
        :param name: Thread name
        """
        threading.Thread.__init__(self, name=name)
        self.window = window
        self.port = port
        self.seq_dig = seq_digits
        self.lock = lock
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.0)

    def __receive_ack(self):
        """
        Waits for an ack, checks its integrity, and if isn't corrupt, delegates it to the window.
        """
        data, address = self.socket.recvfrom(1024)                  # Buffer size = 1024

        if data:
            sequence_number = data.decode()[:self.seq_dig]               # Saves the received sequence number
            checksum = data.decode()[self.seq_dig:]                      # Saves the received checksum
            if checksum == calculate_checksum(sequence_number):          # Just tries to ACK if the sequence number
                with self.lock:                                          # equals to the received checksum
                    self.window.ack(sequence_number, checksum)

    def run(self):
        self.socket.bind(('0.0.0.0', self.port))                         # Connection is always open
        self.socket.settimeout(90)

        while not self.window.has_finished():                            # Wait for ACKs while the window has pending
            self.__receive_ack()                                         # packages.
            time.sleep(0.1)
        print("ReceiverThread :: Stopped waiting for ACKs")
        return 0
