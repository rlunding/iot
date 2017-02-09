import sys
import random

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
from config import Config
from forms import JoinForm, SearchForm
from util import get_free_port, parse_docstring
from concurrent.futures import ThreadPoolExecutor
from time import sleep

executor = ThreadPoolExecutor(2)

app = Flask(__name__)
app.config.from_object(Config())

node = None


@app.route('/')
def home():
    """Homepage
    Show all information about the node

    :returns: html page with node information
    """
    join_form = JoinForm()
    search_form = SearchForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
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


@app.route('/successor/<int:key>', methods=['GET'])
def find_successor(key):
    """Successor for a key

    Return the node responsible for a given key.

    :param key: they key to search for
    :returns: {'successor': true, 'key': successor.key, 'ip': successor.ip, 'port': successor.port} if success,
    otherwise {'successor': false}
    """
    successor_node = node.find_successor(key)
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'ip': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


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
    """Create a new post.
    Form Data: title, content, authorid.
    """
    join_form = JoinForm()
    if join_form.validate_on_submit():
        join_ip = request.form.get('ip')
        join_port = request.form.get('port')
        node.join(join_ip, join_port)
        flash('Successfully join network', 'success')
        return redirect(url_for('home'))
    search_form = SearchForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           search_form=search_form)


@app.route('/search', methods=['POST'])
def search():
    """
    Search for the successor node responsible for a given key.

    :returns:
    """
    search_form = SearchForm()
    if search_form.validate_on_submit():
        result_node = node.find_successor(int(request.form.get('key')))
        output = "{0}:{1}, key={2}".format(result_node.ip, result_node.port, result_node.key)
        flash(output, 'success')
        return redirect(url_for('home'))
    join_form = JoinForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           search_form=search_form)


@app.route('/doc', defaults={'response': 'html'}, methods=['GET'])
@app.route('/doc/<string:response>', methods=['GET'])
def site_map(response):
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
    print("Stabilize")
    node.stabilize()
    node.update_successor_list()
    node.check_predecessor()
    sleep(3 + random.uniform(0, 5))
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
