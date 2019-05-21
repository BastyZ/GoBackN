import threading
import time


class Receiver(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

        self.counter = 5

    def run(self):
        while self.counter > 0:
            # TODO: wait for ACK
            # TODO: check ACK integrity
            # TODO: notify window of ack received
            # TODO: update window
            # TODO: compute timeout
            print("Receiver counter =", self.counter)
            self.counter -= 1
            time.sleep(1)
