from chord.util import encode_address


class Node:
    """
    Class representing a peer in the network
    """

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.key = encode_address(ip, port)
        self.successor = None
        self.predecessor = None

    def get_key(self) -> int:
        return self.key

    def get_successor(self, key) -> 'Node':
        # Find the successor of the peer
        # return: Address of the peer
        return self.successor

    def get_predecessor(self) -> 'Node':
        # Find the predecessor of the peer
        # Address of the peer
        return self.predecessor

    def lookup(self, key):
        pass

    def join(self, ip: str, port: int):
        # Join the peer with the id to the chord-network
        pass

    def leave(self):
        self.successor = None
        self.predecessor = None

    def stabilize(self):
        pass
