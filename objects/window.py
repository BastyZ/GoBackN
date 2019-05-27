from objects.checksum import calculate_checksum
from threading import Lock
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
# Lock used based on https://stackoverflow.com/a/10525433


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list):
        self.sequence_digits = sequence_digits
        self.window_size = window_size
        self.window_start = 0
        self.window_last = 0
        self.last_ack = 0
        self.lock = Lock()
        self.timer = Timer
        self.seqn = 1  # This marks the last sequence number
        self.packages = package_list

        self.window = []

        # TODO: create window place for timeouts determination

    def __create_message(self, message, sequence_number):
        sequence_number_padded = str(sequence_number).zfill(self.sequence_digits)
        checksum = calculate_checksum(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def has_packages(self):
        return False

    def get_next_package(self):
        return None

    def load_next(self):
        # add package to window
        with self.lock:
            if self.window_last + 1 >= len(self.packages):
                pass
            elif self.window_last - self.window_start < self.window_size:  # There's packages to send & wnd isn't full
                # We can load a package to the window
                self.window_last += 1
                # [ sequence number, checksum, package data ]
                self.window.append(
                    [
                        self.seqn + self.window_last,  # Sequence number of last on window
                        calculate_checksum(self.packages[self.seqn]),  # Checksum of package
                        self.packages[self.seqn]  # Package itself
                    ])

    def ack(self, seq_num):
        with self.lock:
            window_min_seqn = self.window[0][0]  # First element's sequence number
            if int(seq_num) < int(window_min_seqn):
                # We really don't care
                pass
            else:
                self.lock.release()
                self.advance(seq_num)

    def advance(self, seq_num):
        with self.lock:
            while seq_num == self.window[0][0]:
                self.window.pop(0)  # destroy first
                # TODO: Reset timer
                self.load_next()
