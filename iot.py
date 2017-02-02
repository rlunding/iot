import sys

from flask import (
    Flask,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
    request
)
from flask_apscheduler import APScheduler
from chord.node import Node
from config import Config
from forms import JoinForm, StabilizeForm
from util import get_free_port


app = Flask(__name__)
app.config.from_object(Config())

node = None


@app.route('/')
def home():
    join_form = JoinForm()
    stabilize_form = StabilizeForm()
    return render_template('home.html', node=node, join_form=join_form, stabilize_form=stabilize_form)


@app.route('/successor', methods=['GET'])
def successor():
    successor_node = node.successor
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'id': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


@app.route('/predecessor', methods=['GET'])
def predecessor():
    predecessor_node = node.predecessor
    if predecessor_node:
        return jsonify({'predecessor': True, 'key': predecessor_node.key, 'id': predecessor_node.ip, 'port': predecessor_node.port})
    return jsonify({'predecessor': False})


@app.route('/successor/<int:key>', methods=['GET'])
def find_successor(key):
    successor_node = node.find_successor(key)
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'ip': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


@app.route('/notify', methods=['POST'])
def notify():
    pred_ip = request.form.get('ip')
    pred_port = request.form.get('port')
    print("ip", pred_ip)
    print("port", pred_port)
    node.notify(Node(pred_ip, pred_port))
    return jsonify({'success': True})


@app.route('/stabilize', methods=['POST'])
def stabilize():
    node.stabilize()
    return redirect(url_for('home'))


@app.route('/join', methods=['POST'])
def join():
    form = JoinForm()
    if form.validate_on_submit():
        join_ip = request.form.get('ip')
        join_port = request.form.get('port')
        node.join(join_ip, join_port)
        flash('Successfully join network', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', node=node, form=form)


def stabilize2():
    print('stabilize')
#    node.stabilize()

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000 #None
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if port is None:
        port = get_free_port()

    node = Node(host, port)
    node.successor = node

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host=host, port=port)



    #now = datetime.now()
    #ip = json.loads(requests.get('http://ip.jsontest.com').text)['ip']
    #return jsonify({'now': now, 'hello': 'Hello World!', 'port': port, 'ip': ip})


#@app.route('/on')
#def on():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'on'}).content


#@app.route('/off')
#def off():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'off'}).content
