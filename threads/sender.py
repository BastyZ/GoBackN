import threading
import time
import socket


class Sender(threading.Thread):
    def __init__(self, window, dest_ip, port, condition):
        threading.Thread.__init__(self)
        self.window = window
        self.dest_ip = dest_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.condition = condition
        # TODO: create window for timeouts determination

    def __send_package(self, package):
        server_address = (self.dest_ip, self.port)

        try:
            self.socket.sendto(package.encode(), server_address)
        finally:
            self.socket.close()

    def retransmit_packages(self):
        self.window.stop_timer()
        self.window.start_timer()
        packages = self.window.get_queued_packages()
        for package in packages:
            self.__send_package(package)

    def run(self):
        while not self.window.has_finished():
            while self.window.is_full():
                self.condition.wait()

            package = self.window.get_next_package()
            self.__send_package(package)
            time.sleep(0.1)
            # TODO: save timestamp for this package and send
            # TODO: activate timer

        self.__send_package("")       # Send empty package to finish
        print("Message was sent")


