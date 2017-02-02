import sys

from flask import (
    Flask,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for
)
from flask_apscheduler import APScheduler
from chord.node import Node
from config import Config
from forms import JoinForm
from util import get_free_port


app = Flask(__name__)
app.config.from_object(Config())

node = None


@app.route('/')
def home():
    join_form = JoinForm()
    return render_template('home.html', node=node, form=join_form)


@app.route('/successor', methods=['GET'])
def successor():
    successor_node = node.successor
    if successor_node:
        return jsonify({'key': successor_node.key, 'id': successor_node.ip, 'port': successor_node.port})
    return jsonify({})


@app.route('/join', methods=['POST'])
def join():
    form = JoinForm()
    if form.validate_on_submit():
        flash('Successfully join network', 'success')
        # TODO: make actual join
        return redirect(url_for('home'))
    return render_template('home.html', node=node, form=form)


def stabilize():
    print('stabilize')

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000 #None
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if port is None:
        port = get_free_port()

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    node = Node(host, port)

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
