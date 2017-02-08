import sys
import collections

from flask import (
    Flask,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app
)
from flask_apscheduler import APScheduler
from chord.node import Node
from config import Config
from forms import JoinForm, StabilizeForm, SearchForm
from util import get_free_port, parse_docstring


app = Flask(__name__)
app.config.from_object(Config())

node = None


@app.route('/')
def home():
    """Show the node status"""
    join_form = JoinForm()
    search_form = SearchForm()
    stabilize_form = StabilizeForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           search_form=search_form,
                           stabilize_form=stabilize_form)


@app.route('/successor', methods=['GET'])
def successor():
    """Return the successor"""
    successor_node = node.successor
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'ip': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


@app.route('/predecessor', methods=['GET'])
def predecessor():
    predecessor_node = node.predecessor
    if predecessor_node:
        return jsonify({'predecessor': True, 'key': predecessor_node.key, 'ip': predecessor_node.ip, 'port': predecessor_node.port})
    return jsonify({'predecessor': False})


@app.route('/successor/<int:key>', methods=['GET'])
def find_successor(key):
    """Return the node responsible for a given key.

    :param key:
    :returns: {'successor': true, 'key': successor.key, 'ip': successor.ip, 'port': successor.port} if success, otherwise {'successor': false}
    """
    successor_node = node.find_successor(key)
    if successor_node:
        return jsonify({'successor': True, 'key': successor_node.key, 'ip': successor_node.ip, 'port': successor_node.port})
    return jsonify({'successor': False})


@app.route('/notify', methods=['POST'])
def notify():
    pred_ip = request.form.get('ip')
    pred_port = request.form.get('port')
    node.notify(Node(pred_ip, pred_port))
    return jsonify({'success': True})


@app.route('/stabilize', methods=['POST'])
def stabilize():
    """short

    long

    :param hest: some hest
    :param gris: some gris
    :return: return something
    """
    node.stabilize()
    return redirect(url_for('home'))


@app.route('/succlist', methods=['POST'])
def succ_list():
    """Update successor list & predecessor

    Update a nodes successor list and check if the predecessor is still alive

    :returns: {'success': true}
    """
    node.update_successor_list()
    node.check_predecessor()
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
    stabilize_form = StabilizeForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           search_form=search_form,
                           stabilize_form=stabilize_form)


@app.route('/search', methods=['POST'])
def search():
    """
    Search for the successor node responsible for a given key.

    :return:
    """
    search_form = SearchForm()
    if search_form.validate_on_submit():
        result_node = node.find_successor(int(request.form.get('key')))
        output = "{0}:{1}, key={2}".format(result_node.ip, result_node.port, result_node.key)
        flash(output, 'success')
        return redirect(url_for('home'))
    join_form = JoinForm()
    stabilize_form = StabilizeForm()
    return render_template('home.html',
                           node=node,
                           join_form=join_form,
                           search_form=search_form,
                           stabilize_form=stabilize_form)


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
    #scheduler.init_app(app)
    #scheduler.start()

    #app.config['SERVER_NAME'] = host + ":" + str(port)
    app.run(host=host, port=port, threaded=True)



    #now = datetime.now()
    #ip = json.loads(requests.get('http://ip.jsontest.com').text)['ip']
    #return jsonify({'now': now, 'hello': 'Hello World!', 'port': port, 'ip': ip})


#@app.route('/on')
#def on():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'on'}).content


#@app.route('/off')
#def off():
#    return requests.post('https://api.particle.io/v1/devices/170030000f47353138383138/led?access_token=8239b3935d2f4c43fef1ba2a03c1112a2ea1f1ec', data={'arg': 'off'}).content
