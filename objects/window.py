from objects.checksum import calculate_checksum
from datetime import datetime


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list, condition, karn_calculator):
        """

        :param sequence_digits:
        :param window_size:
        :param package_list:
        :param condition:
        :param karn_calculator:
        """
        self.sequence_digits = sequence_digits

        self.window = list()
        self.window_max_size = window_size
        self.window_index = 0

        self.packages = package_list
        self.package_index = 0

        self.sender = None
        self.condition = condition

        self.karn_calculator = karn_calculator

        self.finished = False

    def set_sender(self, sender):
        """

        :param sender:
        :return:
        """
        self.sender = sender

    def __create_message(self, message, sequence_number):
        sequence_number_padded = str(sequence_number).zfill(self.sequence_digits)
        checksum = calculate_checksum(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def is_fully_sent(self):
        response = self.window_index >= len(self.window)
        return response

    def set_finished(self):
        self.finished = True
        with self.condition:
            self.condition.notifyAll()

    def has_finished(self):
        if self.finished:
            print("Window :: Getting Out of the loop")
        return self.finished

    def get_next_package(self):
        response = self.__create_message(
            self.window[self.window_index]["package"],
            self.window[self.window_index]["sequence_number"]
        )

        # Stamp time of retrieval
        self.window[self.window_index]["shipping_time"] = datetime.now()
        self.window_index += 1
        return response

    def get_queued_packages(self):
        """
        Method used by the sender when
        :return:
        """
        response = []  # Final response
        for package in self.window:
            package["retransmitted"] = True
            response.append(
                self.__create_message(
                    package["package"],
                    package["sequence_number"]
                )
            )
        return response

    def fulfill(self):
        """
        Method used by the sender at the beginning to fulfill the window with a first chunk of packages
        :return:
        """
        can_advance = True
        while can_advance:
            can_advance = self.load_next()
            print("Window :: Package loaded (wnd size:{} | max: {})".format(len(self.window), self.window_max_size))
        return

    def load_next(self):
        """
        Method used to load the next available package at the list of packages to the window. Not only the package will
        be loaded, this method loads for every package a dict object with the following fields {sequence_number,
        checksum, package, retransmitted, shipping_time}.
        :return:
        """
        # If there is a gap in the window and we have not consumed all the packages from the list of packages
        # then load package from the list of packages to the window. We ignore all other cases.
        if len(self.window) < self.window_max_size and self.package_index < len(self.packages):
            self.window.append(
                dict(
                    sequence_number=str(self.package_index % 10 ** self.sequence_digits).zfill(self.sequence_digits),
                    checksum=calculate_checksum(self.packages[self.package_index]),
                    package=self.packages[self.package_index],
                    retransmitted=False,
                    shipping_time=None
                )
            )
            self.package_index += 1
            return True
        return False

    def ack(self, ack_seq_num, ack_checksum):
        """

        :param ack_seq_num:
        :param ack_checksum:
        :return:
        """
        # Sequence number of the first package of the window
        first = int(self.window[0]["sequence_number"])

        # Sequence number of the last package of the window
        last = int(
            self.window[len(self.window) - 1]["sequence_number"])

        ack_lt_fst = int(ack_seq_num) < first            # ACK sequence number less than windows first sequence number
        ack_gt_lst = int(ack_seq_num) > last             # ACK sequence number greater than windows last sequence number

        if first < last and (ack_lt_fst or ack_gt_lst):    # The received sequence number does not belongs to the window
            return False
        elif first > last and ack_lt_fst and ack_gt_lst:   # The received sequence number does not belongs to the window
            return False

        print("ReceiverThread :: Received ACK N° {} | checksum {}".format(ack_seq_num, ack_checksum))

        for pack in self.window:                                            # Look in the window for the package
            if int(ack_seq_num) == int(pack["sequence_number"]):            # with the received sequence number

                if not pack["retransmitted"]:                               # If it has not been retransmitted
                    sample_rtt = (                                          # then we update the RTT using the Karn
                            datetime.now() - pack["shipping_time"]          # Calculator
                    ).total_seconds()
                    self.karn_calculator.update_timeout_interval(sample_rtt)

                print("Window :: Advancing ... ", ack_seq_num)
                self.advance(ack_seq_num)

                print(f"window_len: {len(self.window)} || window_index: {self.window_index}")
                if len(self.window) == 0:
                    print("Window :: Last ACK received")
                    self.set_finished()
                with self.condition:
                    self.condition.notifyAll()

                break                                                       # Stop for loop because package found
        return True

    def advance(self, sequence_number):
        """
        Advances until the given sequence number, this method assumes the given sequence number belongs to an element
        inside the window. If the given sequence number its different from the sequence number of the first element in
        the window then is assumed that the packages with previous sequence numbers were received.
        :param sequence_number:
        :return:
        """
        # The received sequence number is not at the beginning of the window
        if sequence_number != self.window[0]["sequence_number"]:
            print("Window :: Advancing from {} to {}".format(self.window[0]["sequence_number"], sequence_number))

        next_sequence_number = (int(sequence_number) + 1) % (10 ** self.sequence_digits)
        first_sequence_number = int(self.window[0]["sequence_number"])
        print("next sq = {} and first sq = {}".format(next_sequence_number, first_sequence_number))

        # Advances until the next sequence number (if exists)
        while len(self.window) > 0 and next_sequence_number != first_sequence_number:
            print("Window :: Window's first is", self.window[0]["sequence_number"])
            self.window.pop(0)                                              # Destroys the first window element
            self.window_index = max(0, self.window_index - 1)
            if len(self.window) > 0:
                first_sequence_number = int(self.window[0]["sequence_number"])
            self.load_next()                                                # Tries to load a package
