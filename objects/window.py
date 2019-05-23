from objects import checksum as check

from threading import Lock
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
# Lock used based on https://stackoverflow.com/a/10525433


class SendWindow:
    def __init__(self, cwnd, sequence_exp, package_list):
        self.w_size = cwnd
        self.w_start = 0
        self.w_last = 0
        self.last_ack = 0
        self.lock = Lock()
        self.timer = Timer
        self.seqn = 1
        self.packages = package_list

        self.window = []

    def load_next(self):
        with self.lock:
            if self.w_last + 1 >= len(self.packages):
                # Send empty package
                self.send_ending()
            elif self.w_last - self.w_start < self.w_size:
                # We can load a package to the window
                self.w_last += 1
                self.seqn += 1
                self.window.append([self.seqn, check.calculate_checksum(self.packages[next_p]), self.packages[next_p]])

    def ack(self, seq_num):
        with self.lock:
            window_min_seqn = self.window[0][0]
            if int(seq_num) < int(window_min_seqn):
                # We really don't care
                pass
            else:
                self.advance(seq_num)

    def send_ending(self):
        # TODO: Send an empty package
        pass

    def advance(self, seq_num):
        # TODO: advance till seq_num == window[0][0]
        pass
