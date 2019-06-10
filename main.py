from flask import Flask, jsonify
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World!"})


@app.route('/roi', methods=['GET'])
def roi():
    with open('sample.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)


if __name__ == '__main__':
    app.run()
