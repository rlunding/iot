import requests
import json
from flask import (
    Flask,
    jsonify
)

app = Flask(__name__)


@app.route('/')
def home():
    port = 5000
    nodes = []
    for i in range(0, 50):
        url = 'http://127.0.0.1:{0}/successor'.format(port)
        data = json.loads(requests.get(url).text)

        port = data['port']
        if port in nodes:
            break

        nodes.append(data['port'])  # + data['ip'], data['port']
    return jsonify({'nodes_length': len(nodes), 'nodes': nodes})


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5500)
