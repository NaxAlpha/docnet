import json
import os
from uuid import uuid4

from flask import *

from rpc import ClassifierClient

app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')


@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create():
    fid = str(uuid4())
    request.files['image'].save(os.path.join('data', fid + '.jpg'))
    client = ClassifierClient()
    client.call_async(fid)
    return jsonify(dict(id=fid))


@app.route('/serve/<fid>', methods=['GET'])
def serve(fid):
    return send_from_directory('data', fid + '.jpg')


@app.route('/status', methods=['POST'])
def status():
    out = []
    ids = request.get_json(force=True)
    for fid in ids:
        result_file = os.path.join('data', fid + '.json')
        if os.path.isfile(result_file):
            with open(result_file) as f:
                data = json.load(f)
            out.append({
                'id': fid,
                'status': True,
                'class': data[0][0],
                'score': data[0][1]
            })
        else:
            out.append({
                'id': fid,
                'status': False,
                'class': 'UNKNOWN',
                'score': 0
            })
    return jsonify(out)


if __name__ == '__main__':
    app.run(debug=True)

