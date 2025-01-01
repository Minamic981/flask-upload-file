from flask import render_template, request, jsonify
from routes import routes_bp
from services.s3_service import upload_files_to_s3, list_files_in_s3, s3_client
from botocore.exceptions import ClientError
import os
@routes_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@routes_bp.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'GET':
        return jsonify({"message": "Use POST to upload files."}), 200
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files part"}), 400

        files = request.files.getlist('files')
        uploaded_files = upload_files_to_s3(files)

        if not uploaded_files:
            return jsonify({"error": "No files uploaded"}), 400

        return jsonify({"message": "Files uploaded successfully", "uploaded_files": uploaded_files}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@routes_bp.route('/files', methods=['GET'])
def list_files():
    try:
        files = list_files_in_s3()
        return render_template('files.html', files=files)
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
    
BUCKET_NAME = os.getenv("BUCKET_NAME")
@routes_bp.route('/delete_file/<file_name>', methods=['DELETE'])
def delete_file(file_name):
    try:
        # Delete the file from S3
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        return jsonify({"message": f"File '{file_name}' deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/delete_all_files', methods=['DELETE'])
def delete_all_files():
    try:
        # List all files in the bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
        return jsonify({"message": "All files deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500