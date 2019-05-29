from objects.checksum import calculate_checksum as checksum_of
from threading import Lock   # Lock used based on https://docs.python.org/3/library/threading.html#with-locks
from threading import Timer  # https://docs.python.org/3/library/threading.html#timer-objects
from datetime import datetime


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list, condition):
        self.sequence_digits = sequence_digits
        self.window_size = window_size
        self.window_index = 0
        self.package_index = 0
        self.window_last = -1  # [0,window_size]
        self.last_ack = 0
        self.lock = Lock()

        self.condition = condition
        self.estimated_rtt = 0.0         # 0 seconds as the default round time trip
        self.dev_rtt = 0.0               # 0 seconds as the default round time trip standard deviation
        self.timeout_interval = 1.0      # 1 second as the default Timeout Interval
        self.first_flag = True
        self.finished = False

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
        self.timer = Timer(self.timeout_interval, self.callback, [self.sender])
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def __create_message(self, message, sequence_number):
        sequence_number_padded = str(sequence_number).zfill(self.sequence_digits)
        checksum = checksum_of(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def __update_timeout_interval(self, sample_rtt):
        if self.first_flag:
            self.first_flag = False
            self.estimated_rtt = sample_rtt
            self.dev_rtt = sample_rtt / 2
            self.timeout_interval = self.estimated_rtt + max(1.0, 4 * self.dev_rtt)
        else:
            alpha = 0.125
            beta = 0.25
            self.estimated_rtt = (1 - alpha) * self.estimated_rtt + alpha * sample_rtt
            self.dev_rtt = (1 - beta) * self.dev_rtt + beta * abs(sample_rtt - self.estimated_rtt)
            self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt

    def duplicate_timeout(self):
        self.timeout_interval = 2 * self.timeout_interval

    def is_fully_sent(self):
        response = self.window_index >= len(self.window)
        return response

    def set_finished(self):
        self.finished = True
        self.stop_timer()
        with self.condition:
            self.condition.notifyAll()

    def has_finished(self):
        with self.lock:
            if self.finished:
                print("Window :: Getting Out of the loop")
            end_condition = self.finished
        return end_condition

    def get_next_package(self):
        with self.lock:
            response = self.__create_message(
                self.window[self.window_index][2],      # Package
                self.window[self.window_index][0]       # Sequence number
            )

            # Stamp time of retrieval
            self.window[self.window_index][4] = datetime.now()
            self.window_index += 1
        return response

    def get_queued_packages(self):
        with self.lock:
            response = []  # Final response
            for package in self.window:
                package[3] = True                           # mark it as retransmitted
                response.append(
                    self.__create_message(
                        package[2],                         # Message
                        package[0]                          # Sequence Number
                    )
                )
        return response

    def fulfill(self):
        with self.lock:
            while len(self.window) < self.window_size and self.package_index < len(self.packages):
                self.load_next()
                print("Window :: Package loaded (wnd size:{} | max: {})".format(len(self.window), self.window_size))
        return

    def load_next(self):
        # add package to window
        if len(self.window) < self.window_size and self.package_index < len(self.packages):
            # We can load a packages to the window
            # window = [ sequence number, checksum, package data, retransmitted flag ]
            self.window.append(
                [
                    str.zfill(str(self.package_index % 10**self.sequence_digits), 2),                    # Sequence number of last on window
                    checksum_of(self.packages[self.package_index]),  # Checksum of package
                    self.packages[self.package_index],               # Package itself
                    False,                                           # Retransmitted flag
                    None                                             # Date saving
                ])
            self.window_last += 1
            self.package_index += 1
        else:
            # In any other case we do nothing, because self.window is full
            pass

    def ack(self, ack_seq_num, checksum):
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

                print("Window :: Received ACK")
                for pack in self.window:
                    if int(ack_seq_num) == int(pack[0]) and checksum == checksum_of(ack_seq_num):
                        if not pack[3]:                       # If it wasn't retransmitted
                            # Update rtt
                            sample_rtt = (
                                datetime.now() - pack[4]      # Sent - Acked delta
                            ).total_seconds()
                            self.__update_timeout_interval(sample_rtt)
                        print("Window :: Advancing ... ", ack_seq_num)
                        if ack_seq_num == '41':
                            print("")
                        self.advance(ack_seq_num)
                        print(f"window_len: {len(self.window)} || window_index: {self.window_index}")
                        if checksum_of(self.window[len(self.window) - 1][0]) == checksum_of(ack_seq_num)\
                                and len(self.window) == 1:
                            print("Window :: Last ACK received")
                            self.set_finished()
                        with self.condition:
                            self.condition.notifyAll()

    def advance(self, seq_num):
        print("Window :: Advancing from {} to {}".format(self.window[0][0], seq_num))
        while len(self.window) > 0 and seq_num != self.window[0][0]:
            print("Window :: Window's first is", self.window[0][0])
            self.window.pop(0)                                      # destroys the first window element
            self.window_last -= 1
            self.window_index -= 1
            self.window_index = abs(self.window_index)
            self.seqn = (self.seqn + 1) % 10**self.sequence_digits
            self.stop_timer()
            self.load_next()
            self.start_timer()
        print("Window :: Advanced until {}".format(seq_num))
