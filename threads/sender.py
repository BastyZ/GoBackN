import threading
import socket


class Sender(threading.Thread):
    def __init__(self, window, dest_ip, port, lock, condition, karn_calculator, name):
        """
        Subclass of threading.Thread, implements the sending thread of Go Back N algorithm
        :param window: Window used in Go Back N algorithm
        :param dest_ip: Server IP
        :param port: Port used by the Server to receive Packages
        :param lock: Lock used to avoid data races when using the window
        :param condition: Condition used to make Sender sleep when window is full
        :param name: Thread name
        """
        threading.Thread.__init__(self, name=name)
        self.__window = window                          # Window used in Go Back N algorithm
        self.__dest_ip = dest_ip                        # Server IP
        self.__port = port                              # Port used by the Server to receive Packages
        self.__lock = lock                              # Lock used to avoid data races when using the window
        self.__condition = condition                    # Condition used to make Sender sleep when window is full
        self.__karn_calculator = karn_calculator        # Class used to calculate the timeouts
        self.__timer = None                             # Timer used to retransmit packages

    def __send_package(self, package):
        """
        Sends the given package to the server
        :param package: Package to be sent to the server. It must be a string where the first characters must be the
        sequence number followed by the checksum of the message and the message itself. The maximum length of package
        is 1024 bytes.
        :return:
        """
        server_address = (self.__dest_ip, self.__port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_socket:
            send_socket.sendto(package.encode(), server_address)

    def retransmit_packages(self):
        """
        Retransmit window packages taking care of data races by using a Lock to access the Window.
        :return:
        """
        with self.__lock:
            if self.__window.has_finished():                             # If there are no message to retransmit just
                pass                                                     # pass
            else:
                if not self.__karn_calculator.has_sent_first_package():  # If the first message hasn't been sent then
                    self.__karn_calculator.duplicate_timeout()           # duplicates the timeout

                packages = self.__window.get_queued_packages()           # Get all packages in the window
                if len(packages) > 0:
                    print(f"SenderThread :: Retransmitting package {packages[0][:self.__window.sequence_digits]} "
                          f"to {packages[-1][:self.__window.sequence_digits]}")
                    print(f"SenderThreat ::          Timeout : {self.__karn_calculator.get_current_timeout()}")

                    self.set_timer()                                         # Sets a new timer
                    for package in packages:                                 # Retransmit every package in the window
                        self.__send_package(package)

    def set_timer(self):
        """
        Given the current delay saved in the KarnCalculator, sets a timeout to retransmit the window packages. If there
        was started another timeout this method will cancel that one before starting this.
        :return:
        """
        if self.__timer:                                                 # If already exists a timer, just cancels it
            self.__timer.cancel()
        self.__timer = threading.Timer(self.__karn_calculator.get_current_timeout(),
                                       self.retransmit_packages)         # Creates a new timer
        self.__timer.start()                                             # Starts the timer

    def run(self):
        with self.__lock:
            self.__window.fulfill()
        print("SenderThread :: Window Fulfilled")

        self.set_timer()
        while not self.__window.has_finished():
            with self.__condition:
                while self.__window.is_fully_sent() and not self.__window.has_finished():
                    print("SenderThread :: Go to sleep")
                    self.__condition.wait()

            with self.__lock:
                if not self.__window.has_finished():
                    package = self.__window.get_next_package()
                    self.__send_package(package)
            print("SenderThread :: package sent: {}".format(package[:35]))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
        self.__send_package("")       # Send empty package to finish
        print("SenderThread :: Last Message was sent")
        return 0


