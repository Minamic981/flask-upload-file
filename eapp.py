import boto3
from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Configure your S3 bucket and AWS credentials
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

@app.route('/')
def index():
    return render_template('eexample.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No files part"
    
    files = request.files.getlist('files')  # Get list of files
    responses = []
    
    for file in files:
        if file.filename == '':
            responses.append(f"No selected file for {file.filename}")
            continue
        
        original_filename = file.filename
        
        # Save chunks of the file locally in the /tmp directory
        index = 1
        chunk_filenames = []
        while True:
            chunk = file.stream.read(CHUNK_SIZE)
            if not chunk:
                break

            chunk_filename = f"{original_filename}.part{index}"
            chunk_path = os.path.join('/tmp', chunk_filename)
            try:
                # Save the chunk locally
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                chunk_filenames.append(chunk_path)  # Keep track of chunk file paths
                index += 1
            except Exception as e:
                return f"Error saving chunk {chunk_filename} locally: {e}"

        # After all chunks are saved locally, merge them into one file locally
        try:
            merged_file_path = os.path.join('/tmp', original_filename)  # Path for merged file
            merge_chunks_locally(chunk_filenames, merged_file_path)
            
            # Upload the merged file to S3
            s3_key = f"uploads/{original_filename}"
            s3_client.upload_file(merged_file_path, BUCKET_NAME, s3_key)
            
            # Clean up temporary chunk files
            for chunk_file in chunk_filenames:
                os.remove(chunk_file)
            
            # Clean up merged file from /tmp
            os.remove(merged_file_path)

            responses.append(f"File {original_filename} uploaded and merged successfully into S3!")
        except Exception as e:
            responses.append(f"Error merging chunks or uploading file for {original_filename}: {e}")

    # Return responses for all uploaded files
    return "<br>".join(responses)


def merge_chunks_locally(chunk_filenames, merged_file_path):
    """
    Merge chunks stored in the local filesystem into a single file.
    Assumes the chunks are stored as part1, part2, ..., partN.
    """
    with open(merged_file_path, 'wb') as merged_file:
        for chunk_filename in chunk_filenames:
            with open(chunk_filename, 'rb') as chunk_file:
                merged_file.write(chunk_file.read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)