import hashlib


def calculate_checksum(message):
    """
    Computes the checksum (md5) of a given string.

    :param message: Given string
    :return: Checksum of the given string
    """
    checksum = hashlib.md5(message.encode()).hexdigest()
    return checksum
