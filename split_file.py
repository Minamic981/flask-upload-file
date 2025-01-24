import os

def split_file(file_path, chunk_size=1024 * 1024):
    """
    Splits the given file into chunks of the specified size.

    Args:
        file_path (str): Path to the input file.
        chunk_size (int): Size of each chunk in bytes (default is 1 MB).
    """
    # Ensure the file exists
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return

    # Get the file name and directory
    file_dir, file_name = os.path.split(file_path)
    base_name, ext = os.path.splitext(file_name)
    output_dir = os.path.join(file_dir, f"{base_name}_chunks")

    # Create the output directory for chunks
    os.makedirs(output_dir, exist_ok=True)

    # Split the file into chunks
    with open(file_path, "rb") as f:
        chunk_number = 1
        while chunk := f.read(chunk_size):
            chunk_file_path = os.path.join(output_dir, f"{chunk_number}")
            with open(chunk_file_path, "wb") as chunk_file:
                chunk_file.write(chunk)
            print(f"Created chunk: {chunk_file_path}")
            chunk_number += 1

    print(f"File split complete. Chunks saved in: {output_dir}")


# Example usage
# Replace 'path/to/your/file.ext' with your file's path
import sys
split_file(sys.argv[1])