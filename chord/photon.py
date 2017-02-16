from chord.util import encode_key


class Photon:

    def __init__(self, photon_id: int):
        self.photon_id = photon_id
        self.key = encode_key(str(photon_id))

    def get_light_value(self) -> str:
        # TODO: make get request to photon to get the light value
        return str(42)

    def __str__(self):
        return "(id: " + str(self.photon_id) + ", key:" + str(self.key) + ")"

    def __repr__(self):
        return self.__str__()