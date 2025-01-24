def generate_file_low_cpu_optimized(size_mb, file_path):
    base_chunk = b'a' * 10
    block = base_chunk * 1024
    repetitions = (size_mb * 1024 * 1024) // len(block)

    with open(file_path, 'wb') as f:
        for _ in range(repetitions):
            f.write(block)
            
generate_file_low_cpu_optimized(300, '/tmp/o.txt')