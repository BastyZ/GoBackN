from threads.sender import Sender
from threads.receiver import Receiver


class Server:
    def __init__(self, dest_ip, filename, window_size, package_size, sequence_digits, receive_port, send_port):
        self.dest_ip = dest_ip
        self.filename = filename
        self.window_size = window_size
        self.package_size = package_size
        self.sequence_number = sequence_digits
        self.receive_port = receive_port
        self.send_port = send_port

        self.sender = Sender(filename, dest_ip, send_port, window_size, package_size, sequence_digits)
        self.receiver = Receiver(receive_port)

    def run(self):
        self.receiver.start()
        self.sender.start()

        self.receiver.join()
        self.sender.join()


