import os
import asyncio
import httpx
from sys import argv

# Define the server endpoint
SERVER_URL = 'http://192.168.3.128:5000/upload'  # Replace with your server URL

# Path to the file you want to upload
file_path = argv[1]  # Replace with the file you want to upload

# Split the file into chunks
chunk_size = 1024 * 1024  # 1MB chunks, you can adjust the size
filename = os.path.basename(file_path)
total_chunks = (os.path.getsize(file_path) + chunk_size - 1) // chunk_size  # Total chunks

# Function to upload a single chunk asynchronously using httpx
async def upload_chunk(client, file, chunk_number, total_chunks):
    # Open the file and read the chunk data
    with open(file, 'rb') as f:
        f.seek(chunk_number * chunk_size)
        chunk_data = f.read(chunk_size)
    
    # Prepare the data to be sent
    files = {'file': (filename, chunk_data)}
    data = {
        'filename': filename,
        'chunkNumber': str(chunk_number + 1),  # Chunks are 1-indexed in the server
        'totalChunks': str(total_chunks)
    }

    # Send the request using httpx.AsyncClient
    response = await client.post(SERVER_URL, data=data, files=files)

    # Check if the upload was successful
    if response.status_code == 200:
        json_response = response.json()
        print(f"Successfully uploaded chunk {chunk_number + 1} of {total_chunks}: {json_response}")
    else:
        print(f"Failed to upload chunk {chunk_number + 1}. Error: {response.status_code}, {response.text}")

# Main function to upload all chunks sequentially
async def upload_file():
    # Create the AsyncClient session for all requests
    async with httpx.AsyncClient() as client:
        # Upload chunks sequentially to ensure correct order
        for chunk_number in range(total_chunks):
            await upload_chunk(client, file_path, chunk_number, total_chunks)
    
    print("File upload complete!")

# Run the file upload asynchronously
if __name__ == '__main__':
    asyncio.run(upload_file())