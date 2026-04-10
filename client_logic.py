import os

CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks

def split_file(file_bytes, filename):
    """
    Simulates splitting a file into chunks and saving them locally.
    """
    chunk_paths = []
    total_size = len(file_bytes)
    
    # --- NEW CODE: Create the directory if it doesn't exist ---
    if not os.path.exists("temp_chunks"):
        os.makedirs("temp_chunks")
    # ----------------------------------------------------------
    
    num_chunks = (total_size // CHUNK_SIZE) + (1 if total_size % CHUNK_SIZE > 0 else 0)
    
    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, total_size)
        chunk_data = file_bytes[start:end]
        
        chunk_name = f"{filename}_part{i+1}"
        chunk_path = f"temp_chunks/{chunk_name}"
        
        with open(chunk_path, 'wb') as f:
            f.write(chunk_data)
        
        chunk_paths.append(chunk_name)
    
    return chunk_paths

def stitch_file(filename, chunk_names, output_dir="."):
    """
    Simulates downloading chunks and merging them back together.
    """
    output_path = os.path.join(output_dir, f"downloaded_{filename}")
    
    with open(output_path, 'wb') as outfile:
        for chunk_name in chunk_names:
            chunk_path = f"temp_chunks/{chunk_name}"
            if os.path.exists(chunk_path):
                with open(chunk_path, 'rb') as infile:
                    outfile.write(infile.read())
            else:
                return False, f"Missing chunk: {chunk_name}"
                
    return True, output_path
