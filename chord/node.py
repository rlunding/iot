from chord.util import encode_address
import requests
import json

from config import INTERVAL

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

    @classmethod
    def _in_interval(cls, start: int, stop: int, key: int):
        if start < stop:
            return start < key <= stop
        else:
            return start < key < pow(10, INTERVAL) or 0 <= key <= stop

    @classmethod
    def _make_successor_request(cls, node: 'Node', key: int) -> 'Node':
        url = 'http://{0}:{1}/successor/{2}'.format(node.ip, node.port, key)
        data = json.loads(requests.get(url).text)
        return Node(data['ip'], data['port'])

    @classmethod
    def _make_predecessor_request(cls, node: 'Node') -> 'Node':
        url = 'http://{0}:{1}/predecessor'.format(node.ip, node.port)
        data = json.loads(requests.get(url).text)
        if data['predecessor']:
            return Node(data['ip'], data['port'])
        return None

    def get_key(self) -> int:
        return self.key

    def find_successor(self, key) -> 'Node':
        # Find the successor of the peer
        # return: Address of the peer
        if self._in_interval(self.key, self.successor.key, key):
            return self.successor
        return self._make_successor_request(self.successor, key)

    def join(self, ip: str, port: int):
        # Join the peer with the id to the chord-network
        self.predecessor = None
        self.successor = self._make_successor_request(Node(ip, port), self.key)

    def leave(self):
        self.successor = self
        self.predecessor = None

    def lookup(self, key):
        pass

    def notify(self, node: 'Node'):
        if not self.predecessor or self._in_interval(self.predecessor.key, self.key, node.key):
            self.predecessor = node

    def stabilize(self):
        if self.key != self.successor.key:
            x = self._make_predecessor_request(self.successor)
            if x and self._in_interval(self.key, self.successor.key, x.key):
                self.successor = x
            url = 'http://{0}:{1}/notify'.format(self.successor.ip, self.successor.port)
            requests.post(url, data={'ip': self.ip, 'port': self.port})  # TODO: perhaps check for answer?
        else:
            if self.predecessor and self._in_interval(self.key, self.successor.key, self.predecessor.key):
                self.successor = self.predecessor
            self.notify(self)
