from flask import Flask, jsonify, request as req
from . import repl

app = Flask(__name__)


@app.route('/execute', methods=['POST'])
def execute_code():
    code = req.form['code']
    content, stdout = repl.execute(code)

    return jsonify({'content': content, 'stdout': stdout.rstrip()})


def start():
    app.run(host='0.0.0.0', port=8080, debug=True)
