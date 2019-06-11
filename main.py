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

app = Flask(__name__)
CORS(app)

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
    parts = name.split('.', 1)
    return parts[0] + '/image.' + parts[1]


@app.route('/image/<fileName>/url', methods=['POST'])
def get_upload_url(fileName):
    url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            "Bucket": BUCKET,
            "Key": image_path(fileName.split('.', 1)[0]) + 'image.ome.tif',
            "ContentType": 'image/tiff'
        },
        ExpiresIn=7200)
    print('UPLOAD URL: ' + url)
    return jsonify({"url": url})


@app.route('/image/<name>/url', methods=['GET'])
def get_signed_url(name):
    url = s3_client.generate_presigned_url('get_object',
                                           Params={
                                               "Bucket": BUCKET,
                                               "Key": image_path(name) +
                                               'image.ome.tif',
                                               "ContentType": 'image/tiff'
                                           },
                                           ExpiresIn=7200)
    print('DOWNLOAD URL: ' + url)
    return jsonify({"url": url})


def image_path(name):
    return 'data/' + name + '/'


@app.route('/images', methods=['GET'])
def get_images():
    response = s3_client.list_objects(Bucket=BUCKET, Prefix='data')
    print(response)
    return jsonify({"listing": response["Contents"]})


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
