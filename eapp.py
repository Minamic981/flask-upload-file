import boto3
from botocore.config import Config
from flask import Flask, request, jsonify
import os
import shutil

s3_client = boto3.client('s3',
                         endpoint_url="https://n1d2.fra202.idrivee2-98.com",
                         aws_access_key_id="apELPELYSuMIfC4GMu0v",
                         aws_secret_access_key="QIdUzrinsZkEYnAUYVRjgucpG2OWkdiKh7G3X2m3",
                         config=Config(signature_version='s3v4')
                         )

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
BUCKET_NAME = 'uploads'
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)

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
    chunk_dir = os.path.join(UPLOAD_FOLDER, filename + '_chunks')
    os.makedirs(chunk_dir, exist_ok=True)

    # Save the chunk to the temporary directory
    chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_number}')
    file.save(chunk_path)

    # Check if all chunks are uploaded (only start assembling when all chunks are uploaded)
    if len(os.listdir(chunk_dir)) == total_chunks:
        try:
            assembled_file_path = os.path.join(UPLOAD_FOLDER, filename)
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
            return jsonify({'message': 'Upload complete', 'file_path': assembled_file_path})

        except Exception as e:
            return jsonify({'error': f'Error assembling file: {str(e)}'}), 500

    return jsonify({'message': f'Chunk {chunk_number} uploaded'}), 200

@app.route('/pres',methods=['POST'])
def presigned_url():
    v = request.get_json()
    filename = v['filename']
    presigned_url = s3_client.generate_presigned_url('put_object',
                                                         Params={'Bucket': BUCKET_NAME, 'Key': filename},
                                                         ExpiresIn=3600)  # URL expires in 1 hour
    return jsonify({'pres': presigned_url})
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)