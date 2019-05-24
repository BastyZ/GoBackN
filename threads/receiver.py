import threading
import time
import socket


class Receiver(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __receive_ack(self):
        # TODO: check if the port below is correct
        data, address = self.socket.recvfrom(1024)

        if data:
            print("ACK recibido", data.decode())

    def run(self):
        running = True
        self.socket.bind(('0.0.0.0', self.port))

        # TODO: change timeout according to formula
        self.socket.settimeout(90)
        while running:
            # TODO: wait for ACK
            # TODO: check ACK integrity
            # TODO: notify window of ack received
            # TODO: update window
            # TODO: compute timeout
            self.__receive_ack()
            time.sleep(0.1)
