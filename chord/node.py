from chord.util import encode_address
import requests
import json

from config import INTERVAL, SUCCESSOR_LIST_SIZE


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
        self.successor_list = []

    @classmethod
    def _in_interval(cls, start: int, stop: int, key: int):
        if start < stop:
            return start < key <= stop
        else:
            return start < key < pow(10, INTERVAL) or 0 <= key <= stop

    @classmethod
    def _make_successor_request(cls, node: 'Node', key: int) -> 'Node':
        if key:
            url = 'http://{0}:{1}/successor/{2}'.format(node.ip, node.port, key)
        else:
            url = 'http://{0}:{1}/successor'.format(node.ip, node.port)
        try:
            data = json.loads(requests.get(url).text)
        except:
            return None
        return Node(data['ip'], data['port'])

    def _make_predecessor_request(self) -> 'Node':
        url = 'http://{0}:{1}/predecessor'.format(self.successor.ip, self.successor.port)
        try:
            data = json.loads(requests.get(url).text)
        except:
            self.set_new_successor()
            if self.key != self.successor.key:
                return self._make_predecessor_request()
            return None
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
        result = self._make_successor_request(self.successor, key)
        if not result:
            self.update_successor_list() #TODO: correct to do this here?
            return self.find_successor(key)
        else:
            return result

    def join(self, ip: str, port: int):
        # Join the peer with the id to the chord-network
        self.predecessor = None
        self.successor = self._make_successor_request(Node(ip, port), self.key)
        self.successor_list = []

    def leave(self):
        self.predecessor = None
        self.successor = self
        self.successor_list = []

    def lookup(self, key):
        pass

    def notify(self, node: 'Node'):
        if not self.predecessor or self._in_interval(self.predecessor.key, self.key, node.key):
            self.predecessor = node

    def stabilize(self):
        if self.key != self.successor.key:
            x = self._make_predecessor_request()
            if x and self._in_interval(self.key, self.successor.key, x.key):
                self.successor = x
            url = 'http://{0}:{1}/notify'.format(self.successor.ip, self.successor.port)
            requests.post(url, data={'ip': self.ip, 'port': self.port})  # TODO: perhaps check for answer?
        else:
            if self.predecessor and self._in_interval(self.key, self.successor.key, self.predecessor.key):
                self.successor = self.predecessor
            self.notify(self)

    def update_successor_list(self):
        self.successor_list = [] # TODO: bug, perhaps don't delete the list completely
        succ = self.successor
        for i in range(0, SUCCESSOR_LIST_SIZE):
            if self.key == succ.key:
                break
            result = self._make_successor_request(succ, None)
            if result and self.key != result.key:
                self.successor_list.append(result)
                succ = result

    def set_new_successor(self):
        if len(self.successor_list) > 0:
            self.successor = self.successor_list.pop(0)
        else:
            self.leave()

    def check_predecessor(self):
        try:
            url = 'http://{0}:{1}/successor'.format(self.predecessor.ip, self.predecessor.port)
            requests.get(url)
        except:
            self.predecessor = None
