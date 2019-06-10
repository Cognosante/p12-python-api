import logging
import json
from flask import Flask, jsonify
import boto3
from botocore.exceptions import ClientError
app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World!"})


@app.route('/roi', methods=['GET'])
def roi():
    with open('sample.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)


@app.route('/image/<name>', methods=['POST'])
def get_signed_url(name):
    s3_client = boto3.client('s3')
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={
                                                   "Bucket": "cgs-p12",
                                                   "Key": name
                                               },
                                               ExpiresIn=3600)
    except ClientError as e:
        logging.error(e)
        return None
    return jsonify({"url": url})


if __name__ == '__main__':
    app.run()
