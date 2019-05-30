
class KarnCalculator:
    def __init__(self):
        self.__estimated_rtt = None
        self.__dev_rtt = None
        self.__timeout_interval = 1.0      # 1 second as the default Timeout Interval
        self.__first_package_sent = False

    def has_sent_first_package(self):
        """
        Return true if the first package of the file was sent.

        :return: Boolean
        """
        return self.__first_package_sent

    def duplicate_timeout(self):
        """
        Duplicates timeout interval according to Karn's Algorithm, used when first package is retransmitted.
        """
        self.__timeout_interval *= 2

    def update_timeout_interval(self, sample_rtt):
        """
        Computes timeout interval according to Karn's Algorithm using smoothed round-trip time of a package,
        based on RFC 6298 https://tools.ietf.org/html/rfc6298.

        :param sample_rtt: smoothed round-trip time
        """
        if not self.__first_package_sent:
            self.__first_package_sent = True
            self.__estimated_rtt = sample_rtt
            self.__dev_rtt = sample_rtt / 2
            self.__timeout_interval = self.__estimated_rtt + max(1.0, 4 * self.__dev_rtt)
        else:
            alpha = 0.125
            beta = 0.25
            self.__estimated_rtt = (1 - alpha) * self.__estimated_rtt + alpha * sample_rtt
            self.__dev_rtt = (1 - beta) * self.__dev_rtt + beta * abs(sample_rtt - self.__estimated_rtt)
            self.__timeout_interval = self.__estimated_rtt + 4 * self.__dev_rtt

    def get_current_timeout(self):
        """
        Returns timeout interval.

        :return: timeout interval
        """
        return self.__timeout_interval
