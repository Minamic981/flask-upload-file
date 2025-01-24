import os
import httpx
import boto3
from botocore.config import Config
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from os import getenv as env, path as opath, rmdir
app = Flask(__name__)
load_dotenv()
endpoint_url = env('ENDPOINT_URL')
aws_access_key_id = env('AWS_ACCESS_KEY_ID')
aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = env('AWS_BUCKET_NAME')
TEMP_FOLDER = '/tmp/'
s3_client = boto3.client('s3',
                        endpoint_url=endpoint_url,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        config=Config(signature_version='s3v4')
                        )

def upload_file_to_s3(filename):
    presigned_url = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=800)
    # Open the file in binary mode and send it with the PUT request
    with open(os.path.join(TEMP_FOLDER, filename),'rb') as file_data:
        response = httpx.put(presigned_url, data=file_data)
    
    # Check if the upload was successful
    if response.status_code == 200:
        return jsonify({'status': f'Upload successful {filename}'})
    else:
        return jsonify(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

@app.route('/')
def index():
    return render_template('eexample.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Handle form data
    file = request.files['file']
    filename = request.form.get('filename')
    chunk_number = request.form.get('chunkNumber')
    total_chunks = request.form.get('totalChunks')

    # Ensure all required fields are present
    if not all([chunk_number, total_chunks, filename, file]):
        return jsonify({'error': 'Missing required parameters'}), 400

    chunk_number = int(chunk_number)
    total_chunks = int(total_chunks)

    # Create a temporary directory for chunks
    chunk_dir = os.path.join(TEMP_FOLDER, filename + '_chunks')
    os.makedirs(chunk_dir, exist_ok=True)

    # Save the chunk to the temporary directory
    chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_number}')
    file.save(chunk_path)

    # Check if all chunks are uploaded (only start assembling when all chunks are uploaded)
    if len(os.listdir(chunk_dir)) == total_chunks:
        try:
            assembled_file_path = os.path.join(TEMP_FOLDER, filename)
            with open(assembled_file_path, 'wb') as assembled_file:
                for i in range(1, total_chunks + 1):
                    chunk_file_path = os.path.join(chunk_dir, f'chunk_{i}')
                    if not os.path.exists(chunk_file_path):
                        return jsonify({'error': f'Missing chunk: {i}'}), 400

                    with open(chunk_file_path, 'rb') as chunk_file:
                        assembled_file.write(chunk_file.read())

            # Clean up chunks after successful assembly
            for chunk_file in os.listdir(chunk_dir):
                os.remove(os.path.join(chunk_dir, chunk_file))
            os.rmdir(chunk_dir)
            return upload_file_to_s3(filename)

        except Exception as e:
            return jsonify({'error': f'Error assembling file: {str(e)}'}), 500

    return jsonify({'message': f'Chunk {chunk_number} uploaded'}), 200

app.run('0.0.0.0', debug=True)