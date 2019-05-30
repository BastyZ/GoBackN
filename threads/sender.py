import threading
import time
import socket


class Sender(threading.Thread):
    def __init__(self, window, dest_ip, port, lock, condition, name):
        threading.Thread.__init__(self, name=name)
        self.window = window
        self.dest_ip = dest_ip
        self.port = port
        self.lock = lock
        self.condition = condition

    def __send_package(self, package):
        server_address = (self.dest_ip, self.port)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_socket:
            send_socket.sendto(package.encode(), server_address)

    def retransmit_packages(self):
        with self.lock:
            self.window.stop_timer()
            if self.window.has_sent_first_package():
                self.window.duplicate_timeout()
            self.window.start_timer()
            packages = self.window.get_queued_packages()
            print(f"SenderThread :: Retransmitting package {packages[0][:self.window.sequence_digits]} to {packages[-1][:self.window.sequence_digits]}")
            print(f"SenderThreat ::          Timeout : {self.window.timeout_interval}")
            for package in packages:
                self.__send_package(package)

    def run(self):
        first_time_flag = True
        with self.lock:
            self.window.fulfill()
        print("SenderThread :: Window Fulfilled")
        while not self.window.has_finished():
            with self.condition:
                while self.window.is_fully_sent() and not self.window.has_finished():
                    print("SenderThread :: Go to sleep")
                    self.condition.wait()
                    if self.window.has_finished():
                        self.__send_package("")  # Send empty package to finish

            if self.window.has_finished():
                break
            if first_time_flag:
                first_time_flag = False
                with self.lock:
                    self.window.start_timer()
            package = self.window.get_next_package()
            self.__send_package(package)
            print("SenderThread :: package sent: {}".format(package[:35]))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
        self.__send_package("")       # Send empty package to finish
        print("SenderThread :: Last Message was sent")
        return 0


