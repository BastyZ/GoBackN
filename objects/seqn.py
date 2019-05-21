from threading import Lock as Lock
# Lock used based on https://stackoverflow.com/a/10525433


class SequenceNumber:
    def __init__(self, exp):  # Exponent it's for computing max sequence number
        self.exp = exp
        self.max = 10**exp - 1
        self.number = 0
        self.lock = Lock()

    def next(self):
        with self.lock:
            print("Lock Acquired")
            if self.number + 1 < self.max:
                self.number += 1
        return self.get()

    def next_int(self):
        return int(self.next())

    def get(self):
        # FIXME: use numpy to give a more elegant solution
        with self.lock:
            print("Lock Acquired by str")
            # Returns number with exp - 1 characters
            actual_exp = 0
            num = self.number
            while num > 0:
                num /= 10
                num = int(num)
                actual_exp += 1
            zeros_quantity = self.exp - actual_exp
            string = ""
            if self.number == 0:
                zeros_quantity -= 1
            while zeros_quantity > 0:
                string += "0"
                zeros_quantity -= 1
            return string + str(self.number)
