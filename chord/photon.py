import requests
import json
import sqlite3 as sql

from chord.util import encode_key


class Photon:

    def __init__(self, photon_id: str):
        self.photon_id = photon_id
        self.key = encode_key(photon_id)

    def get_light_value(self, port) -> str:
        con = sql.connect('data/' + str(port) + '.db')
        cur = con.execute("SELECT * FROM measurement WHERE id = ?  ORDER BY date DESC", [self.key])
        rv = cur.fetchone()
        print(rv)
        try:
            return rv[2]
        except:
            return "None"

    def pull_light_value(self) -> str:
        try:
            url = "https://api.particle.io/v1/devices/{0}/analogvalue?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec".format(self.photon_id)
            data = json.loads(requests.get(url, timeout=1).text)
            return str(data['result'])
        except:
            return "42" #"None"

    def __str__(self):
        return "(id: " + self.photon_id + ", key:" + str(self.key) + ")"

    def __repr__(self):
        return self.__str__()
