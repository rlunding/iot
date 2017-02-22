import requests
import json

from chord.util import encode_key


class Photon:

    def __init__(self, photon_id: str):
        self.photon_id = photon_id
        self.key = encode_key(photon_id)

    def get_light_value(self) -> str:
        try:
            url = "https://api.particle.io/v1/devices/{0}/analogvalue?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec".format(self.photon_id)
            data = json.loads(requests.get(url).text)
            return str(data['result'])
        except:
            return "None"

    def __str__(self):
        return "(id: " + self.photon_id + ", key:" + str(self.key) + ")"

    def __repr__(self):
        return self.__str__()
