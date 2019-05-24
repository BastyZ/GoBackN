import threading
import time
import socket
from objects.checksum import calculate_checksum
from objects.window import SendWindow


class Sender(threading.Thread):
    def __init__(self, filename, dest_ip, port, window_size, package_size, sequence_digits):
        threading.Thread.__init__(self)
        self.filename = filename
        self.message = self.__get_file_content()
        self.dest_ip = dest_ip
        self.port = port
        self.window_size = window_size
        self.raw_packages = []
        self.package_size = package_size  # on bytes
        self.sequence_digits = sequence_digits

        # TODO: create window for timeouts determination

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

    def __create_message(self, message, sequence_number):
        sequence_number_padded = str(sequence_number).zfill(self.sequence_digits)
        checksum = calculate_checksum(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def __send_packet(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.dest_ip, self.port)

        try:
            sock.sendto(message.encode(), server_address)
        finally:
            sock.close()

    def run(self):
        self.raw_packages = [self.message[i:i+self.package_size] for i in range(0, len(self.message),
                                                                                self.package_size)]

        # while self.w_last_acked < len(self.raw_packages):  # While we still have not ACKed everything
        print("len(parts) =", len(self.raw_packages))

        sequence_number = 0
        window = SendWindow(self.window_size, self.raw_packages)
        while sequence_number < len(self.raw_packages):
            # TODO: determinate seq number
            # TODO: add package to window
            # TODO: save timestamp for this package and send
            # TODO: activate timer
            message = self.__create_message(self.raw_packages[sequence_number], sequence_number)
            self.__send_packet(message)
            print("sending ", self.raw_packages[sequence_number])
            time.sleep(0.1)

            sequence_number += 1

        self.__send_packet("")       # Send empty package to finish
        print("Message was sent")
