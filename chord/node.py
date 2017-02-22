

from chord.util import encode_address, encode_key, in_interval
from chord.finger_table import FingerTable
from chord.photon import Photon
import requests
import json
import random
import time

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
        self.successor_list_index_update = 0
        self.finger_table = FingerTable(self.key)
        self.last_request_key = None
        self.last_request_owner = []
        self.finger_index_update = 0
        self.photons = []

    def _make_successor_request(self, node: 'Node', key: int, start_key: int = None) -> 'Node':
        """Make a request to a node go get the successor responsible for a key"""
        if start_key is None:
            start_key = self.key

        if key:
            url = 'http://{0}:{1}/successor/{2}/{3}'.format(node.ip, node.port, key, start_key)
        else:
            url = 'http://{0}:{1}/successor'.format(node.ip, node.port)
        try:
            data = json.loads(requests.get(url).text)
        except:
            return None
        if data is not None:
            if data['successor'] is True:
                return Node(data['ip'], data['port'])
        return None

    def get_key(self) -> int:
        return self.key

    def _use_fingertable(self, key: int, start_key: int):
        # If we have already seen this request key it means
        # that we are in an endless loop and we need to get out
        # Push the job to our successor
        if start_key in self.last_request_owner or key == self.last_request_key:
            # return self._make_successor_request(self.successor, key), "Start key {0} same as last request key".format(
            #    start_key)
            return None, "Start key {0} same as last request key".format(start_key)
        self.last_request_key = key
        self.last_request_owner.append(start_key)

        # The key is not in our interval so we forward the request
        # to the best fitting peer in our finger table.
        # Find the peer closest in the finger table
        node = self.closest_preceding_finger(key)

        # if for some reason the finger table returns our own key,
        # forward the call to the successor as we have already
        # verified that we are not done (key is not in our interval)
        if node.key == self.key:
            # return self._make_successor_request(self.successor, key), "Finger table returned own key: {0}".format(
            #    node.key)
            return None, "Finger table returned own key: {0}".format(node.key)

        # Request find_successor on this peer
        url = 'http://{0}:{1}/successor/{2}/{3}'.format(node.ip, node.port, key, start_key)
        try:
            print("[{1}] Successor request: {0}".format(url, self.port))
            data = json.loads(requests.get(url).text)
        except:
            return None, "Failed Request (except)"
        if data is not None:
            if data['successor'] is True:
                print('[{1}] Node key returned: {0}'.format(node.key, self.port))
                return Node(data['ip'], data['port']), "Success request"
            if data['successor'] is False:
                return None, data['error']
        return None, "Request data None"

    def _slow_successor(self, key: int, start_key: int):
        url = 'http://{0}:{1}/successor/{2}/{3}'.format(self.successor.ip, self.successor.port, key, start_key)
        try:
            print("[{1}][Slow] Successor request: {0}".format(url, self.port))
            data = json.loads(requests.get(url).text)
        except:
            # Try another successor from the lst
            self.set_new_successor()
            return self._slow_successor(key, start_key)
        if data is not None:
            if data['successor'] is True:
                node = Node(data['ip'], data['port'])
                print('[{1}][Slow] Node key returned: {0}'.format(node.key, self.port))
                return node, "[Slow] Success request"
            if data['successor'] is False:
                return None, data['error']
        return None, "[Slow] Request data None"

    def find_successor(self, key: int, start_key: int, use_fingers=True) -> ('Node', str):
        msg = ""

        # Check if the key is between us an our successor.
        # If that is the case we are done and can return the
        # successor.
        if in_interval(self.key, self.successor.key, key):
            return self.successor, "Self successor"
        # Also check the predecessor
        if self.predecessor is not None:
            if in_interval(self.predecessor.key, self.key, key):
                return Node(self.ip, self.port), "Self predecessor"

        # Trying finger tables first if enabled
        if use_fingers:
            finger_result, msg = self._use_fingertable(key, start_key)
            if finger_result is not None:
                return finger_result, msg

        # Finger table did not return a result or is not enabled
        # Trying slow method to move forward
        slow_result, msg_slow = self._slow_successor(key, start_key)
        if slow_result is not None:
            return slow_result, msg_slow + " : " + msg

        return None, "Everything failed (returned None): " + msg_slow + " : " + msg

    def closest_preceding_finger(self, key):
        print('{1}: Searching finger table for key: {0}'.format(key, self.port))
        node = self.finger_table.closest_preceding_finger(key)
        if node is not None:
            print('{3}: Found node: {0} ({1}) while searching for {2}'.format(node.key, node.port, key, self.port))
            return node
        print('Did not find any match in the finger table...')
        return self

    def join(self, ip: str, port: int):
        # Join the peer with the id to the chord-network
        self.predecessor = None
        while True:
            print("[{0}] Trying to join: {1}".format(self.port, port))
            self.successor = self._make_successor_request(Node(ip, port), self.key)
            if self.successor is not None:
                print("[{0}] Joined".format(self.port))
                break
            print("[{0}] Sleeping...".format(self.port))
            time.sleep(5)

        self.finger_table.update_finger(0, self.successor)
        self.successor_list = []
        self.stabilize()
        self.get_photons_from_successor()

    def leave(self):
        self.predecessor = None
        self.successor = self
        self.successor_list = []

    def notify(self, node: 'Node'):
        if not self.predecessor or in_interval(self.predecessor.key, self.key, node.key):
            self.predecessor = node

    def stabilize(self):
        # clear last request key
        self.last_request_key = None
        self.last_request_owner = []

        if self.key != self.successor.key:
            x = None

            # Request successor for it's predecessor
            url = 'http://{0}:{1}/predecessor'.format(self.successor.ip, self.successor.port)
            try:
                data = json.loads(requests.get(url).text)
            except:
                self.set_new_successor()
                data = None

            if data is not None:
                if data['predecessor']:
                    x = Node(data['ip'], data['port'])

            if x and in_interval(self.key, self.successor.key, x.key):
                self.successor = x

            url = 'http://{0}:{1}/notify'.format(self.successor.ip, self.successor.port)
            requests.post(url, data={'ip': self.ip, 'port': self.port})  # TODO: perhaps check for answer?
        else:
            if self.predecessor and in_interval(self.key, self.successor.key, self.predecessor.key):
                self.successor = self.predecessor
            self.notify(self)
        self.finger_table.update_finger(0, self.successor)

    def update_successor_list(self):
        new_successor_list = []
        succ = self.successor
        for i in range(0, SUCCESSOR_LIST_SIZE):
            if self.key == succ.key:
                break
            result = self._make_successor_request(succ, None)
            if result is None and succ == self.successor:
                self.set_new_successor()
                succ = self.successor
            if result and self.key != result.key:
                new_successor_list.append(result)
                succ = result
        self.successor_list = new_successor_list

    def set_new_successor(self):
        if len(self.successor_list) > 0:
            self.successor = self.successor_list.pop(0)
            self.finger_table.update_finger(0, self.successor)
        else:
            self.leave()

    def check_predecessor(self):
        try:
            url = 'http://{0}:{1}/successor'.format(self.predecessor.ip, self.predecessor.port)
            requests.get(url)
        except:
            self.predecessor = None

    def fix_fingers(self):
        # i = random.randint(0, self.finger_table.max_i) # Find random entry to update
        inc_prob = random.randint(0, 10)

        i = self.finger_index_update
        node, msg = self.find_successor(self.finger_table.keys[i], self.key) # Find correct successor
        if node is not None:
                        self.finger_table.update_finger(i, node) # Update finger table
                        self.finger_index_update = i+1
        else:
            # Finger table has a small change of jumping one index even if this
            # did not get updated.
            if inc_prob == 1:
                self.finger_index_update = i + 1

        if self.finger_index_update > self.finger_table.max_i:
            self.finger_index_update = 0

    def request_photon_add(self, photon_id: str) -> bool:
        node, msg = self.find_successor(encode_key(photon_id), self.key)
        if node is None:
            return False
        if node.key == self.key:
            self.add_photon(photon_id)
            return True
        try:
            url = 'http://{0}:{1}/add_photon'.format(node.ip, node.port)
            requests.post(url, data={'photon_id': photon_id})
            return True
        except:
            return False

    def add_photon(self, photon_id: str):
        photon = Photon(photon_id)
        self.photons.append(photon)
        print(self.port, "Adding photon with id: ", photon_id, "and key:", photon.key)

    def get_photons_from_successor(self):
        url = 'http://{0}:{1}/give_photons'.format(self.successor.ip, self.successor.port)
        data = json.loads(requests.post(url, data={'key': self.key}).text)
        print(self.port, "Got the following photons from successor: ", data['photons'])
        for photon_id in data['photons']:
            print("Adding: ", photon_id)
            self.photons.append(Photon(photon_id))

    def give_photons(self, key: int):
        result = [x.photon_id for x in self.photons if in_interval(self.key, key, x.key)]
        self.photons = [x for x in self.photons if not in_interval(self.key, key, x.key)]

        print(self.port, "Photons left: ", self.photons)
        print(self.port, "Giving photons to: ", key, result)

        return result

    def __str__(self):
        return "(" + self.ip + ":" + str(self.port) + ", " + str(self.key) + ")"

    def __repr__(self):
        return self.__str__()
