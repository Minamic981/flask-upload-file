import requests
import boto3
from botocore.config import Config
from flask import Flask, render_template, jsonify, request as reqf
from dotenv import load_dotenv
from os import getenv as env, path as opath, rmdir
app = Flask(__name__)
load_dotenv()
endpoint_url = env('ENDPOINT_URL', 'https://n1d2.fra202.idrivee2-98.com')
aws_access_key_id = env('AWS_ACCESS_KEY_ID','apELPELYSuMIfC4GMu0v')
aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY', 'QIdUzrinsZkEYnAUYVRjgucpG2OWkdiKh7G3X2m3')
BUCKET_NAME = env('AWS_BUCKET_NAME', 'uploads')
s3_client = boto3.client('s3',
                        endpoint_url=endpoint_url,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        config=Config(signature_version='s3v4')
                        )

def generate_file(size_mb):
    file_path = f'/tmp/{size_mb}.txt'
    if opath.exists(file_path):
        rmdir(file_path)
    base_chunk = b'a' * 10
    block = base_chunk * 1024
    repetitions = (size_mb * 1024 * 1024) // len(block)

    with open(file_path, 'wb') as f:
        for _ in range(repetitions):
            f.write(block)
    return file_path

def upload_file_to_s3(presigned_url, file_path):
    # Open the file in binary mode and send it with the PUT request
    with open(file_path, 'rb') as file_data:
        response = requests.put(presigned_url, data=file_data)
    
    # Check if the upload was successful
    if response.status_code == 200:
        return jsonify({'status': f'Upload successful {file_path}'})
    else:
        return jsonify(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

@app.route('/')
def index():
    return render_template('eexample.html')

import time
@app.route('/s', methods=['POST'])
def s():
    size_mb = int(reqf.get_json()['size_mb'])
    filename = generate_file(size_mb)
    presigned_url = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=800)
    return upload_file_to_s3(presigned_url, filename)
if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)