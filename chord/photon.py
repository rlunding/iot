import requests
import json
import sqlite3 as sql

from chord.util import encode_key


class Photon:

    def __init__(self, photon_id: str):
        self.photon_id = photon_id
        self.key = encode_key(photon_id)

    def get_light_value(self, port: int) -> str:
        con = sql.connect('data/' + str(port) + '.db')
        cur = con.execute("SELECT * FROM measurement WHERE id = ?  ORDER BY date DESC", [self.key])
        rv = cur.fetchone()
        print(rv)
        try:
            return rv[2]
        except:
            return "None"
        finally:
            con.close()

    def get_latest_light_values(self, port: int, last_request: str):
        con = sql.connect('data/' + str(port) + '.db')
        con.row_factory = sql.Row  # This enables column access by name: row['column_name']
        db = con.cursor()
        rows = db.execute("SELECT * FROM measurement WHERE id = ? AND date > ?", [self.key, last_request]).fetchall()
        con.commit()
        con.close()
        print(rows)
        print(json.dumps([dict(x) for x in rows]))
        return json.dumps([dict(x) for x in rows])

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


class PhotonBackup:

    def __init__(self, photon_id: str, node):
        self.photon_id = photon_id
        self.photon_key = encode_key(photon_id)
        self.node = node

    def get_last_poll(self, port):
        con = sql.connect('data/' + str(port) + '.db')
        cur = con.execute("SELECT * FROM measurement WHERE id = ?  ORDER BY date DESC", [self.key])
        rv = cur.fetchone()
        print(rv)
        try:
            return rv[0]
        except:
            return "0"
        finally:
            con.close()

