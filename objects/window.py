from objects.checksum import calculate_checksum as checksum_of
from threading import Lock   # Lock used based on https://stackoverflow.com/a/10525433
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
from datetime import datetime


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list, condition):
        self.sequence_digits = sequence_digits
        self.window_size = window_size
        self.window_index = 0
        self.window_last = 0  # [0,window_size]
        self.last_ack = 0
        self.lock = Lock()

        self.condition = condition
        self.estimated_rtt = 0.0         # 0 seconds as the default round time trip
        self.dev_rtt = 0.0               # 0 seconds as the default round time trip standard deviation
        self.timeout_interval = 1.0      # 1 second as the default Timeout Interval

        self.callback = None
        self.sender = None
        self.timer = None

        self.seqn = 0                    # This marks the first window's package sequence number
        self.packages = package_list
        self.window = []

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

    def is_fully_sent(self):
        return self.window_index <= self.seqn + len(self.window) - 1

    def has_finished(self):
        with self.lock:
            end_condition = len(self.window) == 0 and self.seqn >= len(self.packages)
            self.lock.release()
        return end_condition

    def get_next_package(self):
        with self.lock:
            response = self.__create_message(
                self.window[self.window_index][2],
                self.window[self.window_index][0]
            )  # Package and seqn

            # Stamp time of retrieval
            self.window[self.window_index][4] = datetime.now()

            self.window_index = self.window_index + 1
            self.lock.release()
        return response

    def get_queued_packages(self):
        with self.lock:
            response = []  # Final response
            for package in self.window:
                package[3] = True                           # mark it as retransmitted
                response.append(self.__create_message(
                    package[2],                             # Checksum
                    package[0]                              # Data
                ))
            self.lock.release()
        return response

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
                        False,                                          # Retransmitted flag
                        None                                            # Date saving
                    ])
            else:
                # In any other case we do nothing, because self.window is full
                pass

    def ack(self, ack_seq_num):
        with self.lock:
            first = self.window[0][0]                   # First element's sequence number
            last = self.window[self.window_last][0]     # Last element's sequence number

            ack_lt_fst = int(ack_seq_num) < int(first)  # ack seqn less than windows first
            ack_gt_lst = int(ack_seq_num) > int(last)   # ack seqn greater than windows last

            if first < last and (ack_lt_fst or ack_gt_lst):
                # We really don't care, it's out of the window
                pass
            elif first > last and ack_lt_fst and ack_gt_lst:
                # We really don't care, it's out of the window
                pass
            else:  # It's definitively on the window
                if not self.window[0][4]:                       # If it wasn't retransmitted
                    self.estimated_rtt = (
                        datetime.now() - self.window[0][4]      # Sent - Acked delta
                    ).total_seconds()
                self.lock.release()
                self.advance(ack_seq_num)
                self.condition.notifyAll()

    def advance(self, seq_num):
        with self.lock:
            while seq_num != self.window[0][0]:
                self.window.pop(0)                                      # destroys the first window element
                self.seqn = (self.seqn + 1) % 10**self.sequence_digits
                self.stop_timer()
                self.load_next()
                self.start_timer()
