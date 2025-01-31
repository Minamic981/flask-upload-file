import os
import httpx
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv
from datetime import datetime
from os import getenv as env, path as opath, rmdir
app = Flask(__name__)
load_dotenv()
ENDPOINT_URL = env('ENDPOINT_URL')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = env('AWS_BUCKET_NAME')
TEMP_FOLDER = '/tmp/'
s3_client = boto3.client('s3',
                        endpoint_url=ENDPOINT_URL,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        config=Config(signature_version='s3v4')
                        )

def upload_file_to_s3(filename):
    presigned_url = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=800)
    # Open the file in binary mode and send it with the PUT request
    with open(os.path.join(TEMP_FOLDER, filename),'rb') as file_data:
        response = httpx.put(presigned_url, data=file_data, timeout=30)
    
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
    print(f"message Chunk {chunk_number} uploaded")
    return jsonify({'message': f'Chunk {chunk_number} uploaded'}), 200

@app.route("/getlink")
def get_link():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': f'Error assembling file: {str(e)}'}), 500
    presigned_url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=800)
    return presigned_url

def list_files_in_s3():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key']
                file_url = f"/getrlink/{file_name}"
                # Get the file's upload date (LastModified)
                upload_date = obj['LastModified']
                # Format the upload date in a readable format
                formatted_date = upload_date.strftime('%Y-%m-%d %H:%M:%S')
                files.append({'name': file_name, 'url': file_url, 'upload_date': formatted_date})

            # Sort files by the upload date, most recent first
            files.sort(key=lambda x: datetime.strptime(x['upload_date'], '%Y-%m-%d %H:%M:%S'), reverse=True)

        return files
    except ClientError as e:
        raise Exception(f"AWS S3 error: {e}")

@app.route('/getrlink/<filename>')
def getrlink(filename):
    presigned_url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=800)
    return redirect(presigned_url)
        

@app.route("/files", methods=["GET"])
def list_files():
    try:
        files = list_files_in_s3()
        return render_template("filess.html", files=files)
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@app.route("/delete_file/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    try:
        s3_client.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=file_name)
        return jsonify({"message": f"File '{file_name}' deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Delete all files route
@app.route("/delete_all_files", methods=["DELETE"])
def delete_all_files():
    try:
        response = s3_client.list_objects_v2(Bucket=os.getenv("BUCKET_NAME"))
        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=obj["Key"])
        return jsonify({"message": "All files deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)