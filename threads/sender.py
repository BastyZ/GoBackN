import threading
import time


class Sender(threading.Thread):
    def __init__(self, filename, dest_ip, port, window_size, package_size, sequence_number):
        threading.Thread.__init__(self)
        self.filename = filename
        self.dest_ip = dest_ip
        self.port = port
        self.window_size = window_size
        self.packages = []
        self.package_size = package_size  # on bytes
        self.sequence_number = sequence_number

        # TODO: create window for timeouts determination

        self.counter = -5

    def run(self):
        # TODO: determinate package quantity
        # TODO: create packages list on self.raw_packages
        while self.w_last_acked < len(self.raw_packages):  # While we still have not ACKed everything
            # TODO: determinate seq number
            # TODO: compute checksum
            # TODO: build package
            # TODO: add package to window
            # TODO: save timestamp for this package and send
            # TODO: activate timer
            print("Sender counter =", self.counter)
            self.counter += 1
            time.sleep(1)
        # TODO: send empty package
