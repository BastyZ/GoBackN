import threading
import time
import socket


class Sender(threading.Thread):
    def __init__(self, window, dest_ip, port):
        threading.Thread.__init__(self)
        self.window = window
        self.dest_ip = dest_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # TODO: create window for timeouts determination

    def __send_package(self, package):
        server_address = (self.dest_ip, self.port)

        try:
            self.socket.sendto(package.encode(), server_address)
        finally:
            self.socket.close()

    def run(self):
        while self.window.has_packages():
            # message = self.__create_message(self.raw_packages[sequence_number], sequence_number) # Now its done by
            # the window

            package = self.window.get_next_package()
            self.__send_package(package)
            time.sleep(0.1)
            # TODO: save timestamp for this package and send
            # TODO: activate timer

        self.__send_package("")       # Send empty package to finish
        print("Message was sent")
