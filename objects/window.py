from objects.checksum import calculate_checksum
from datetime import datetime


class SendWindow:
    def __init__(self, sequence_digits, window_size, package_list, condition, karn_calculator):
        """
        Window used on the Go Back N algorithm.

        :param sequence_digits:
        :param window_size:
        :param package_list:
        :param condition:
        :param karn_calculator:
        """
        self.__sequence_digits = sequence_digits

        self.__window = list()
        self.__window_max_size = window_size
        self.__window_index = 0

        self.__packages = package_list
        self.__package_index = 0

        self.__sender = None
        self.__condition = condition

        self.__karn_calculator = karn_calculator

        self.__finished = False

    def set_sender(self, sender):
        """
        Sets sender to retransmit callback.

        :param sender: Sender Thread pointer
        """
        self.__sender = sender

    def __create_message(self, message, sequence_number):
        """
        Constructs the message to be sent to the server, including Sequence number, checksum and Data respectively
        Message length overall must be less than 1024 bytes (characters).

        :param message: Data to be sent
        :param sequence_number: Sequence number
        :return: message (String)
        """
        sequence_number_padded = str(sequence_number).zfill(self.__sequence_digits)
        checksum = calculate_checksum(message)
        return "%s%s%s" % (str(sequence_number_padded), str(checksum), message)

    def is_fully_sent(self):
        """
        Returns True if all the packages on the window were sent.

        :return: Boolean
        """
        return self.__window_index >= len(self.__window)

    def __set_finished(self):
        """
        Marks the process as finished and notifies the Sender.
        """
        self.__finished = True
        with self.__condition:
            self.__condition.notifyAll()

    def has_finished(self):
        """
        Returns the "finished" boolean, true if all packages were received by the server.

        :return: Boolean
        """
        if self.__finished:
            print("Window :: Getting Out of the loop")
        return self.__finished

    def get_next_package(self):
        """
        Method that returns the next package to be sent (not retransmitted).

        :return: Message to be sent to the server
        """
        response = self.__create_message(
            self.__window[self.__window_index]["package"],
            self.__window[self.__window_index]["sequence_number"]
        )

        # Stamp time of retrieval
        self.__window[self.__window_index]["shipping_time"] = datetime.now()
        self.__window_index += 1
        return response

    def get_queued_packages(self):
        """
        Method used by the sender to get packages to retransmit.

        :return: A list of queued packages
        """
        response = []  # Final response
        for package in self.__window:
            package["retransmitted"] = True
            response.append(
                self.__create_message(
                    package["package"],
                    package["sequence_number"]
                )
            )
        print(f"SenderThread :: Retransmitting package {response[0][:self.__sequence_digits]} "
              f"to {response[-1][:self.__sequence_digits]}")
        print(f"SenderThreat ::          Timeout : {self.__karn_calculator.get_current_timeout()}")
        return response

    def fulfill(self):
        """
        Method used by the sender at the beginning to fulfill the window with a first chunk of packages.
        """
        can_advance = True
        while can_advance:
            can_advance = self.load_next()

    def load_next(self):
        """
        Method used to load the next available package at the list of packages to the window. Not only the package will
        be loaded, this method loads for every package a dict object with the following fields {sequence_number,
        checksum, package, retransmitted, shipping_time}.

        :return: True if a package was successfully loaded. (Boolean)
        """
        # If there is a gap in the window and we have not consumed all the packages from the list of packages
        # then load package from the list of packages to the window. We ignore all other cases.
        if len(self.__window) < self.__window_max_size and self.__package_index < len(self.__packages):
            self.__window.append(
                dict(
                    sequence_number=
                    str(self.__package_index % 10 ** self.__sequence_digits).zfill(self.__sequence_digits),
                    checksum=calculate_checksum(self.__packages[self.__package_index]),
                    package=self.__packages[self.__package_index],
                    retransmitted=False,
                    shipping_time=None
                )
            )
            self.__package_index += 1
            return True
        return False

    def ack(self, ack_seq_num, ack_checksum):
        """
        Receives ACK and triggers advance method if this ACK corresponds to one on the window.

        :param ack_seq_num: Sequence Number of the ACK
        :param ack_checksum: Checksum of the ACK (checksum of the sequence number)
        :return: Boolean, true if the ACK was in the window
        """
        # Sequence number of the first package of the window
        first = int(self.__window[0]["sequence_number"])

        # Sequence number of the last package of the window
        last = int(
            self.__window[len(self.__window) - 1]["sequence_number"])

        ack_lt_fst = int(ack_seq_num) < first            # ACK sequence number less than windows first sequence number
        ack_gt_lst = int(ack_seq_num) > last             # ACK sequence number greater than windows last sequence number

        if first < last and (ack_lt_fst or ack_gt_lst):    # The received sequence number does not belongs to the window
            return False
        elif first > last and ack_lt_fst and ack_gt_lst:   # The received sequence number does not belongs to the window
            return False

        print(f"ReceiverThread :: Received ACK N° {ack_seq_num} | checksum {ack_checksum}")

        for pack in self.__window:                                            # Look in the window for the package
            if int(ack_seq_num) == int(pack["sequence_number"]):            # with the received sequence number

                if not pack["retransmitted"]:                               # If it has not been retransmitted
                    sample_rtt = (                                          # then we update the RTT using the Karn
                            datetime.now() - pack["shipping_time"]          # Calculator
                    ).total_seconds()
                    self.__karn_calculator.update_timeout_interval(sample_rtt)
                self.advance(ack_seq_num)

                if len(self.__window) == 0:
                    print("Window :: Last ACK received")
                    self.__set_finished()
                with self.__condition:
                    self.__condition.notifyAll()

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

        next_sequence_number = (int(sequence_number) + 1) % (10 ** self.__sequence_digits)
        first_sequence_number = int(self.__window[0]["sequence_number"])

        # Advances until the next sequence number (if exists)
        while len(self.__window) > 0 and next_sequence_number != first_sequence_number:
            self.__window.pop(0)                                              # Destroys the first window element
            self.__window_index = max(0, self.__window_index - 1)
            if len(self.__window) > 0:
                first_sequence_number = int(self.__window[0]["sequence_number"])
            self.load_next()                                                # Tries to load a package
