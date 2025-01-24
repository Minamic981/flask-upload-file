import requests
import boto3
from botocore.config import Config
from flask import Flask
app = Flask(__name__)
s3_client = boto3.client('s3',
                         endpoint_url="https://n1d2.fra202.idrivee2-98.com",
                         aws_access_key_id="apELPELYSuMIfC4GMu0v",
                         aws_secret_access_key="QIdUzrinsZkEYnAUYVRjgucpG2OWkdiKh7G3X2m3",
                         config=Config(signature_version='s3v4')
                         )

def upload_file_to_s3(presigned_url, file_path):
    # Open the file in binary mode and send it with the PUT request
    with open(file_path, 'rb') as file_data:
        response = requests.put(presigned_url, data=file_data)
    
    # Check if the upload was successful
    if response.status_code == 200:
        print(f"File uploaded successfully to {presigned_url}")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

@app.route('/s')
def s():
    filename = './10mb.txt'
    presigned_url = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'uploads', 'Key': filename},
                                                    ExpiresIn=3600)
    upload_file_to_s3(presigned_url, filename)
if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)