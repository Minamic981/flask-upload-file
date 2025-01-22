from flask import request, jsonify, render_template
from services.s3_service import upload_file_to_s3, list_files_in_s3, s3_client, ENDPOINT_URL , BUCKET_NAME
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
from routes import routes_bp
import os
# File upload route
CHUNK_DIR = 'temp'
@routes_bp.route("/upload", methods=["POST", "GET"])
def upload_file():
    if request.method == "GET":
        return jsonify({"message": "Use POST to upload files."}), 200

    try:
        # Ensure temporary chunk directory exists
        os.makedirs(CHUNK_DIR, exist_ok=True)

        # Extract metadata
        file_name = secure_filename(request.form.get("fileName"))
        chunk_index = int(request.form.get("chunkIndex"))
        total_chunks = int(request.form.get("totalChunks"))

        if not file_name or chunk_index is None or total_chunks is None:
            return jsonify({"error": "Missing file metadata"}), 400

        # Save the chunk
        chunk_path = os.path.join(CHUNK_DIR, f"{file_name}.part{chunk_index}")
        with open(chunk_path, "wb") as chunk_file:
            chunk_file.write(request.files["file"].read())

        # Check if all chunks are uploaded
        uploaded_chunks = len([f for f in os.listdir(CHUNK_DIR) if f.startswith(file_name)])
        if uploaded_chunks == total_chunks:
            # Reassemble chunks
            final_file_path = os.path.join(CHUNK_DIR, file_name)
            with open(final_file_path, "wb") as final_file:
                for i in range(total_chunks):
                    part_path = os.path.join(CHUNK_DIR, f"{file_name}.part{i}")
                    with open(part_path, "rb") as part_file:
                        final_file.write(part_file.read())
                    os.remove(part_path)  # Clean up the chunk

            # Upload to S3
            s3_key = upload_file_to_s3(final_file_path, file_name)

            # Clean up the assembled file
            os.remove(final_file_path)

            return jsonify({"message": "File uploaded successfully", "s3_key": s3_key}), 200

        return jsonify({"message": "Chunk uploaded successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# List files route
@routes_bp.route("/files", methods=["GET"])
def list_files():
    try:
        files = list_files_in_s3()
        return render_template("files.html", files=files)
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# Delete file route
@routes_bp.route("/delete_file/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    try:
        s3_client.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=file_name)
        return jsonify({"message": f"File '{file_name}' deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Delete all files route
@routes_bp.route("/delete_all_files", methods=["DELETE"])
def delete_all_files():
    try:
        response = s3_client.list_objects_v2(Bucket=os.getenv("BUCKET_NAME"))
        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=obj["Key"])
        return jsonify({"message": "All files deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500
    
@routes_bp.route("/get-link", methods=["POST"])
def get_download_link():
    data = request.get_json()
    file_name = data.get("file_name")

    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    try:
        # Construct the direct file URL
        file_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{file_name}"
        return jsonify({"link": file_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500