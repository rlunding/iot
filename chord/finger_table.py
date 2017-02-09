import math

from config import INTERVAL


class FingerTable:

    def __init__(self, key):
        self.key = key
        self.max_i = self.largest_power_of_2(math.pow(10, INTERVAL))
        self.fingers = [None] * (self.max_i + 1)
        self.keys = [self.find_start(i) for i in range(0, self.max_i + 1)]

    @classmethod
    def largest_power_of_2(cls, n: float) -> int:
        """Find the largest power of 2, which is used to determine the size of the finger table"""
        return int(math.log2(n))

    def find_start(self, i) -> int:
        return int((self.key + math.pow(2, i)) % math.pow(10, INTERVAL))

    def update_finger(self, i: int, node):
        self.fingers[i] = node


