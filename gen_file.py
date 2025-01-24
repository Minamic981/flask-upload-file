import os

# Function to create file with specific size
def create_file(file_size_mb):
    # Convert the file size to bytes (1 MB = 1024 * 1024 bytes)
    file_size_bytes = int(file_size_mb * 1024 * 1024)

    # Path where the file will be created
    file_path = f"{int(file_size_mb)}mb.txt"

    # Generate random data of the required size
    with open(file_path, "wb") as file:
        file.write(os.urandom(file_size_bytes))

    # Confirm the file size
    print(f"The file '{file_path}' has been created with size: {os.path.getsize(file_path)} bytes.")

# Get user input for file size in MB
import sys
size_mb = sys.argv[1]
size_mb = float(size_mb)

# Create the file with the user-specified size
create_file(size_mb)