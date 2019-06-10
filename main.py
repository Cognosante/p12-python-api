import logging
import json
from flask import Flask, jsonify
import boto3
from botocore.exceptions import ClientError
from read_roi import read_roi_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

s3_client = boto3.client('s3')

BUCKET = "cgs-p12"


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World!"})


@app.route('/roi', methods=['GET'])
def roi():
    with open('sample.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)


def get_upload_name(name):
    parts = name.split('.',1)
    return 'data/' + parts[0] + '/image.' + parts[1]

@app.route('/image/<name>/url', methods=['GET'])
def get_signed_url(name):
    response = s3_client.generate_presigned_url('put_object',
                                  Params={'Bucket': BUCKET,
                                          'Key':get_upload_name(name)
                                  },
                                  ExpiresIn=600)
    print(response)
    return jsonify({"url": response})


def image_path(name):
    return 'data/' + name + '/'


@app.route('/image/<name>/roi', methods=['GET'])
def get_roi(name):
    listing = s3_client.list_objects(Bucket=BUCKET, Prefix=image_path(name))
    result = []
    for file in listing["Contents"]:
        if (file["Key"].endswith('.roi')):
            print(file["Key"])
            tmp_file = '/tmp/roi_file_tmp.roi'
            with open(tmp_file, 'wb') as f:
                s3_client.download_fileobj(BUCKET, file["Key"], f)
            rois = read_roi_file(tmp_file)
            result.append(rois)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
