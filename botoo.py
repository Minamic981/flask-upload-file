import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask app configuration
app = Flask(__name__)

AWS_BUCKET_NAME = 'uploads'
# Initialize a session using Amazon S3
s3_client = boto3.client('s3',
                         endpoint_url="https://n1d2.fra202.idrivee2-98.com",
                         aws_access_key_id="apELPELYSuMIfC4GMu0v",
                         aws_secret_access_key="QIdUzrinsZkEYnAUYVRjgucpG2OWkdiKh7G3X2m3"
                         )

# Allowable file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return '''
    <html>
    <body>
        <h1>Upload a file to S3</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        # Secure the filename and upload it to S3
        filename = secure_filename(file.filename)
        
        try:
            # Upload the file to the S3 bucket
            s3_client.upload_fileobj(file, AWS_BUCKET_NAME, filename)
            return f"File '{filename}' uploaded successfully to S3!", 200
        except Exception as e:
            return f"Error uploading file: {e}", 500
    else:
        return 'File type not allowed', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)