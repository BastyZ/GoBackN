from objects.checksum import calculate_checksum as checksum_of
from threading import Lock
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
# Lock used based on https://stackoverflow.com/a/10525433


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list):
        self.sequence_digits = sequence_digits
        self.window_size = window_size
        self.window_start = 0
        self.window_last = 0  # [0,window_size]
        self.last_ack = 0
        self.lock = Lock()

        self.estimated_rtt = 0.0         # 0 seconds as the default round time trip
        self.dev_rtt = 0.0               # 0 seconds as the default round time trip standard deviation
        self.timeout_interval = 1.0      # 1 second as the default Timeout Interval

        self.callback = None
        self.sender = None
        self.timer = None

        self.seqn = 1                    # This marks the last sequence number
        self.packages = package_list

        self.window = []

        # TODO: create window place for timeouts determination

    def set_callback(self, callback):
        self.callback = callback

    def set_sender(self, sender):
        self.sender = sender

    def start_timer(self):
        with self.lock:
            self.timer = Timer(self.timeout_interval, self.callback, [self.sender])
            self.timer.start()
            self.lock.release()

    def stop_timer(self):
        with self.lock:
            if self.timer:
                self.timer.cancel()
            self.lock.release()

    def __create_message(self, message, sequence_number):
        sequence_number_padded = str(sequence_number).zfill(self.sequence_digits)
        checksum = checksum_of(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def __update_timeout_interval(self, sample_rtt):
        alpha = 0.125
        beta = 0.25
        self.estimated_rtt = (1 - alpha) * self.estimated_rtt + alpha * sample_rtt
        self.dev_rtt = (1 - beta) * self.dev_rtt + beta * abs(sample_rtt - self.estimated_rtt)
        self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt

    def restart_timer(self):
        self.timer.cancel()

    def duplicate_timeout(self):
        self.timeout_interval = 2 * self.timeout_interval

    def has_finished(self):
        with self.lock:
            end_condition = len(self.window) == 0 and self.seqn >= len(self.packages)
            self.lock.release()
        return end_condition

    def get_next_package(self):
        with self.lock:
            return self.__create_message(
                self.window[0][2],
                self.window[0][0]
            )  # Package and seqn

    def load_next(self):
        # add package to window
        with self.lock:
            if self.seqn + self.window_last + 1 >= len(self.packages):
                pass
            elif len(self.window) < self.window_size:  # There's packages to send & window isn't full
                # We can load a package to the window
                self.window_last += 1
                last_package_seqn = self.seqn + len(self.window)
                # window = [ sequence number, checksum, package data, retransmitted flag ]
                self.window.append(
                    [
                        last_package_seqn,                              # Sequence number of last on window
                        checksum_of(self.packages[last_package_seqn]),  # Checksum of package
                        self.packages[last_package_seqn],               # Package itself
                        0                                               # Retransmitted flag
                    ])
            else:
                # In any other case we do nothing, because self.window is full
                pass

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
                self.seqn += 1
                # TODO: Reset timer
                self.load_next()
