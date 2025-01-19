import boto3
from botocore.client import Config
from services.s3_service import ENDPOINT_URL, ACCESS_KEY, SECRET_KEY

# MinIO server details
minio_endpoint = "http://your-minio-server:9000"  # Replace with your MinIO server URL
access_key = "your-access-key"  # Replace with your MinIO access key
secret_key = "your-secret-key"  # Replace with your MinIO secret key

# Create an S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

# Bucket name
bucket_name = "uploads"  # Replace with your bucket name

# Check versioning status

response = s3_client.get_bucket_versioning(Bucket=bucket_name)
print(response['ResponseMetadata']['HTTPHeaders'].keys())