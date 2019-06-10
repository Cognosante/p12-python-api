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


@app.route('/file/<filename>', methods=['POST'])
def get_signed_url(filename):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={
                                                        "Bucket": "cgs-p12",
                                                        "Key": filename
                                                    },
                                                    ExpiresIn=3600)
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return jsonify({"url": response})


if __name__ == '__main__':
    app.run()
