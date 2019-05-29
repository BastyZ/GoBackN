import hashlib


def calculate_checksum(message):
    checksum = hashlib.md5(message.encode()).hexdigest()
    return checksum
