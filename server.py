import threading
from threads.sender import Sender
from threads.receiver import Receiver
from objects.window import SendWindow


def retransmit_packages(sender):
    sender.retransmit_packages()


class Server:
    def __init__(self, dest_ip, filename, window_size, package_size, sequence_digits, receive_port, send_port):
        self.dest_ip = dest_ip

        self.filename = filename                                              # Path to the file containing the message
        message = self.__get_file_content()                                   # Retrieve message from file
        raw_packages = [message[i:i + package_size] for i in                  # Divides message in packages of size
                        range(0, len(message), package_size)]                 # 'package_size'

        self.lock = threading.Lock()
        self.condition = threading.Condition()                                # Condition used when window is full

        self.window = SendWindow(sequence_digits, window_size,                # Initializes the window
                                 raw_packages, self.condition)

        self.receive_port = receive_port                                      # Port used to receive the ACKs
        self.send_port = send_port                                            # Port used to send the packages

        self.sender = Sender(self.window, dest_ip, send_port,                 # Thread used to send the packages
                             self.lock, self.condition,
                             name="SenderThread")
        self.receiver = Receiver(self.window, receive_port,                   # Thread used to receive the ACKs
                                 sequence_digits, self.lock,
                                 name="ReceiverThread")

        self.window.set_callback(retransmit_packages)
        self.window.set_sender(self.sender)

    def __get_file_content(self):
        content = None
        with open(self.filename, "r", encoding="utf-8") as file:
            try:
                content = file.read()
            except IOError:
                print("There was an error when reading the file: {}".format(self.filename))
            finally:
                file.close()
        print("File content is:")
        print(content)
        return content

    def run(self):
        self.receiver.start()
        self.sender.start()

        self.receiver.join()
        self.sender.join()

        print("CLIENT :: Threads Finished")
        return 0
