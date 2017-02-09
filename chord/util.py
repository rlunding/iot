import hashlib
import math

from config import INTERVAL


def encode_address(ip: str, port: int) -> int:
    """
    Return a sha-256 hash of the ip-address and the port number

    :param ip: address
    :param port: port number
    :return: sha-256 hash
    """
    return encode_key(ip + str(port))


def encode_key(key: str, size=INTERVAL) -> int:
    """
    Return a subset of a sha-256 hash

    :param key:
    :param size:
    :return:
    """
    res = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), base=16)
    if size is not None:
        res //= int((math.pow(10, (int(math.log10(res)) + 1 - size))))
    return res


def in_interval(start: int, stop: int, key: int):
    """Calculate if key is within the interval of start and stop"""
    if start < stop:
        return start < key <= stop
    else:
        return start < key < pow(10, INTERVAL) or 0 <= key <= stop