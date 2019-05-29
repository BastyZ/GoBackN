import threading
import time
import socket


class Sender(threading.Thread):
    def __init__(self, window, dest_ip, port, condition, name):
        threading.Thread.__init__(self, name=name)
        self.window = window
        self.dest_ip = dest_ip
        self.port = port
        self.condition = condition

    def __send_package(self, package):
        server_address = (self.dest_ip, self.port)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_socket:
            send_socket.sendto(package.encode(), server_address)

    def retransmit_packages(self):
        with self.window.lock:
            self.window.stop_timer()
        if self.window.first_flag:
            self.window.duplicate_timeout()
        with self.window.lock:
            self.window.start_timer()
        packages = self.window.get_queued_packages()
        for package in packages:
            self.__send_package(package)
            print(f"SenderThread :: Retransmitting package {package[:self.window.sequence_digits]} {package}")

    def run(self):
        first_time_flag = True
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
                with self.window.lock:
                    self.window.start_timer()
            package = self.window.get_next_package()
            self.__send_package(package)
            print("SenderThread :: package sent: {}".format(package))
            time.sleep(0.5)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
        self.__send_package("")       # Send empty package to finish
        print("SenderThread :: Last Message was sent")
        return 0


