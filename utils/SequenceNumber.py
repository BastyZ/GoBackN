from threading import Lock as Lock
# Lock used based on https://stackoverflow.com/a/10525433


class SequenceNumber:
    def __init__(self, exp):  # Exponent it's for computing max sequence number
        self.max = 10**exp
        self.number = 0
        self.lock = Lock()

    def next(self):
        with self.lock:
            if self.number + 1 < self.max:
                self.number += 1
            num = self.__str__()
            return num

    def __str__(self):
        with self.lock:
            # Returns number as exp characters
            actual_exp = ""
            num = self.number
            while num != 0:
                num /= 10
                actual_exp += "0"
            actual_exp += str(self.number)
            return actual_exp
