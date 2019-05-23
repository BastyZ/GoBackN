import threading
import time
import socket
from objects.checksum import calculate_checksum


class Sender(threading.Thread):
    def __init__(self, filename, dest_ip, port, window_size, package_size, sequence_number):
        threading.Thread.__init__(self)
        self.filename = filename
        self.message = self.__get_file_content()
        self.dest_ip = dest_ip
        self.port = port
        self.window_size = window_size
        self.packages = []
        self.package_size = package_size  # on bytes
        self.sequence_number = sequence_number

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

    def __create_message(self, message, seq_num):
        seq_number_padded = str(seq_num).zfill(2)
        checksum = calculate_checksum(message)
        return "%s%s%s" % (str(seq_number_padded), str(checksum), message)

    def __send_packet(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.dest_ip, self.port)

        try:
            sock.sendto(message.encode(), server_address)
        finally:
            sock.close()

    def run(self):
        parts = [self.message[i:i+30] for i in range(0, len(self.message), 30)]
        # TODO: determinate package quantity
        # TODO: create packages list on self.raw_packages

        # while self.w_last_acked < len(self.raw_packages):  # While we still have not ACKed everything
        print("len(parts) =", len(parts))
        while self.sequence_number < len(parts):
            # TODO: determinate seq number
            # TODO: compute checksum
            # TODO: build package
            # TODO: add package to window
            # TODO: save timestamp for this package and send
            # TODO: activate timer
            message = self.__create_message(parts[self.sequence_number], self.sequence_number)
            self.__send_packet(message)
            print("sending ", parts[self.sequence_number])
            time.sleep(1)

            self.sequence_number += 1

        # TODO: send empty package
        self.__send_packet("")
        print("Message was sent")
