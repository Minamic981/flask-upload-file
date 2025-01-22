import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os
# AWS S3 configuration
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

def upload_files_to_s3(files):
    uploaded_files = []
    for file in files:
        if file.filename == '':
            continue
        file_name = file.filename
        s3_client.upload_fileobj(
            Fileobj=file.stream,
            Bucket=BUCKET_NAME,
            Key=file_name,
            ExtraArgs={'ContentType': file.content_type}
        )
        uploaded_files.append(file_name)
    return uploaded_files

def file_exists_in_s3(file_name):
    try:
        c = s3_client.head_object(Bucket=BUCKET_NAME, Key=file_name)
        return True
    except ClientError as e:
        return False

# Modify filename if file exists
def get_unique_filename(file_name):
    base_name, extension = file_name.rsplit('.', 1)
    counter = 1
    new_file_name = f"{base_name}_{counter}.{extension}"
    while file_exists_in_s3(new_file_name):
        counter += 1
        new_file_name = f"{base_name}_{counter}.{extension}"
    return new_file_name

def upload_file_to_s3(file_path,file_name):
    if file_exists_in_s3(file_name):
        file_name = get_unique_filename(file_name)
    # Upload the file to S3
    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=BUCKET_NAME,
            Key=file_name,
            ExtraArgs={"ContentType": "application/octet-stream"}
        )
        print(f"File uploaded successfully as {file_name}")
    except ClientError as e:
        print(f"Error uploading file: {e}")

def list_files_in_s3():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key']
                file_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{file_name}"
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