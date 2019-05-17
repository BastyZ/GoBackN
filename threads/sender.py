import threading
import time


class Sender(threading.Thread):
    def __init__(self, filename, dest_ip, port, window_size, package_size, sequence_number):
        threading.Thread.__init__(self)
        self.filename = filename
        self.dest_ip = dest_ip
        self.port = port
        self.window_size = window_size
        self.package_size = package_size
        self.sequence_number = sequence_number

        self.counter = 5

    def run(self):
        while self.counter > 0:
            print("Sender counter =", self.counter)
            self.counter -= 1
            time.sleep(1)
