import sys
import random
import logging

from flask import (
    Flask,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
    request
)

from chord.node import Node
from chord.util import encode_key
from config import Config
from forms import JoinForm, SearchForm, AddForm
from util import get_free_port, parse_docstring
from concurrent.futures import ThreadPoolExecutor
from time import sleep

executor = ThreadPoolExecutor(2)

app = Flask(__name__)
app.config.from_object(Config())

node = None


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def home():
    """Homepage

    Show all information about the node

    :returns: html page with node information
    """
    join_form = JoinForm()
    add_form = AddForm()
    search_form = SearchForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           add_form=add_form,
                           search_form=search_form)


@app.route('/successor', methods=['GET'])
def successor():
    """Successor

    Return the successor of a given node

    :returns: {'successor': true, 'key': successor.key, 'ip': successor.ip, 'port': successor.port} if the node have a
    successor, otherwise {'successor': false}.
    """
    successor_node = node.successor
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'ip': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


@app.route('/predecessor', methods=['GET'])
def predecessor():
    """Predecessor

    Return the predecessor of a given node

    :returns: {'predecessor': true, 'key': predecessor.key, 'ip': predecessor.ip, 'port': predecessor.port} if the node
    have a predecessor, otherwise {'predecessor': false}.
    """
    predecessor_node = node.predecessor
    if predecessor_node:
        return jsonify({'predecessor': True, 'key': predecessor_node.key, 'ip': predecessor_node.ip, 'port': predecessor_node.port})
    return jsonify({'predecessor': False})


@app.route('/successor/<int:key>/<int:start_key>/', methods=['GET'])
def find_successor(key, start_key):
    """Successor for a key

    Return the node responsible for a given key.

    :param key: they key to search for
    :param start_key: key for peer starting the request
    :returns: {'successor': true, 'key': successor.key, 'ip': successor.ip, 'port': successor.port,
    'msg': message explaining the request } if success,
    otherwise {'successor': false, 'error': error message}
    """
    if node.key == start_key:
        return jsonify({'successor': False, 'error': 'node.key == start key == {0}'.format(start_key)})

    successor_node, msg, count = node.find_successor(key, start_key)
    if successor_node:
        return jsonify({'successor': True,
                        'key': successor_node.key,
                        'ip': successor_node.ip,
                        'port': successor_node.port,
                        'msg': msg,
                        'count': count})
    return jsonify({'successor': False, 'error': msg})


@app.route('/successor/<int:key>/<int:start_key>/<int:count>', methods=['GET'])
def find_successor_counting(key, start_key, count):
    """Successor for a key

    Return the node responsible for a given key.

    :param key: they key to search for
    :param start_key: key for peer starting the request
    :returns: {'successor': true, 'key': successor.key, 'ip': successor.ip, 'port': successor.port,
    'msg': message explaining the request } if success,
    otherwise {'successor': false, 'error': error message}
    """
    if node.key == start_key:
        return jsonify({'successor': False, 'error': 'node.key == start key == {0}'.format(start_key)})

    successor_node, msg, count = node.find_successor(key, start_key, count)
    if successor_node:
        return jsonify({'successor': True,
                        'key': successor_node.key,
                        'ip': successor_node.ip,
                        'port': successor_node.port,
                        'msg': msg,
                        'count': count})
    return jsonify({'successor': False, 'error': msg})


@app.route('/notify', methods=['POST'])
def notify():
    """Notify

    Call notify on the node to signal that it might be its new predecessor

    :param ip: the ip-address of the node notifying
    :param port: the port of the node notifying
    :returns: {'success': True}
    """
    pred_ip = request.form.get('ip')
    pred_port = request.form.get('port')
    node.notify(Node(pred_ip, pred_port))
    return jsonify({'success': True})


@app.route('/join', methods=['POST'])
def join():
    """Join

    Join the chord-network which the node with the provided ip and port is part of.

    :param ip: the ip-address of the node which should be joined.
    :param port: the port of the node which should be joined.
    :return: html page with node information, possible also with errors if the input is invalid.
    """
    join_form = JoinForm()
    if join_form.validate_on_submit():
        join_ip = request.form.get('ip')
        join_port = request.form.get('port')
        node.join(join_ip, join_port)
        flash('Successfully join network', 'success')
        return redirect(url_for('home'))
    search_form = SearchForm()
    add_form = AddForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           add_form=add_form,
                           search_form=search_form)


@app.route('/request_add_photon', methods=['POST'])
def request_add_photon():
    add_form = AddForm()
    if add_form.validate_on_submit():
        photon_id = request.form.get('photon_id')
        if node.request_photon_add(photon_id):
            key = encode_key(photon_id)
            flash('Successfully added photon to the network, with key: '+str(key), 'success')
        else:
            flash('Failed to add photon to the network', 'danger')
        return redirect(url_for('home'))
    join_form = JoinForm()
    search_form = SearchForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           add_form=add_form,
                           search_form=search_form)


@app.route('/add_photon', methods=['POST'])
def add_photon():
    photon_id = request.form.get('photon_id')
    node.add_photon(photon_id)
    return jsonify({'success': True})


@app.route('/give_photons', methods=['POST'])
def give_photons():
    key = int(request.form.get('key'))
    result = node.give_photons(key)
    return jsonify({'photons': result})


@app.route('/search', methods=['POST'])
def search():
    """Search

    Search for the successor node responsible for a given key.

    :param key: the key of the node which should be found.
    :returns: html page with node information, possible also with errors if the input is invalid.
    """
    search_form = SearchForm()
    if search_form.validate_on_submit():
        result_node, msg, count = node.find_successor(int(request.form.get('key')), node.key)
        if result_node is not None:
            output = "{0}:{1}, key={2}, msg={3}, hop count = {4}".format(result_node.ip, result_node.port, result_node.key, msg, count)
        else:
            output = msg
        flash(output, 'success')
        return redirect(url_for('home'))
    join_form = JoinForm()
    add_form = AddForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           add_form=add_form,
                           search_form=search_form)


@app.route('/closest_finger/<int:key>', methods=['GET'])
def closest_finger(key):
    """Closest finger

    Report the closest preceding finger.

    :param key: the key that is searched for
    :return: json response: {'node_ip': ip, 'node_port': port}
    """
    pf = node.closest_preceding_finger(key)
    return jsonify({'node_ip': pf.ip, 'node_port': pf.port})


@app.route('/api', defaults={'response': 'html'}, methods=['GET'])
@app.route('/api/<string:response>', methods=['GET'])
def api(response):
    """Print available functions.

    Print all available functions and list what parameters they take and what responses they produce.

    :param response: define whether the response should be json or html
    :return:
    """
    endpoints = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints[rule.rule] = parse_docstring(app.view_functions[rule.endpoint].__doc__, rule.methods)
    if response == 'json':
        return jsonify(endpoints)
    return render_template('doc.html', endpoints=endpoints)


def stabilize():
    """Stabilize
    Call stabilize on the node
    """
    node.stabilize()
    node.update_successor_list()
    node.check_predecessor()
    node.fix_fingers()
    sleep(2 + random.uniform(0, 2))
    executor.submit(stabilize)


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000 #None
    join_port = None
    if len(sys.argv) > 2:
        join_port = int(sys.argv[2])
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if port is None:
        port = get_free_port()


    node = Node(host, port)
    node.successor = node

    if join_port:
        node.join(host, join_port)

    executor.submit(stabilize)

    #app.config['SERVER_NAME'] = host + ":" + str(port)
    app.run(host=host, port=port, threaded=True)


#@app.route('/on')
#def on():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'on'}).content


#@app.route('/off')
#def off():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'off'}).content
