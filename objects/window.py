from objects import checksum as check

from threading import Lock
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
# Lock used based on https://stackoverflow.com/a/10525433


class SendWindow:
    def __init__(self, cwnd, package_list):
        self.w_size = cwnd
        self.w_start = 0
        self.w_last = 0
        self.last_ack = 0
        self.lock = Lock()
        self.timer = Timer
        self.seqn = 1  # This marks the last sequence number
        self.packages = package_list

        self.window = []

        # TODO: create window place for timeouts determination
        # TODO: determinate seq number
        # TODO: add package to window
        # TODO: save timestamp for this package and send
        # TODO: activate timer

    def load_next(self):
        with self.lock:
            if self.w_last + 1 >= len(self.packages):
                pass
            elif self.w_last - self.w_start < self.w_size:  # There is packages to send & window isn't full
                # We can load a package to the window
                self.w_last += 1
                self.seqn += 1
                # [ sequence number, checksum, package data ]
                self.window.append([self.seqn, check.calculate_checksum(self.packages[self.seqn]), self.packages[self.seqn]])

    def ack(self, seq_num):
        with self.lock:
            window_min_seqn = self.window[0][0]
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
                self.load_next()
