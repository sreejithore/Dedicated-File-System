import xmlrpc.server
import sqlite3
import os

DB_FILE = "master_metadata.db"

def init_db():
    """Initializes the SQLite database to store metadata."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Table to track which chunks belong to which files, and where they live
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_chunks (
            filename TEXT,
            chunk_name TEXT,
            node_ip TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- RPC EXPOSED FUNCTIONS ---
# These functions can be called over the network by the Client or Data Nodes

def register_file_chunks(filename, chunk_data):
    """
    Called by the Client when uploading. 
    chunk_data is a list of dictionaries: [{'chunk_name': '...', 'node_ip': '...'}, ...]
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        for chunk in chunk_data:
            cursor.execute("INSERT INTO file_chunks (filename, chunk_name, node_ip) VALUES (?, ?, ?)",
                           (filename, chunk['chunk_name'], chunk['node_ip']))
        conn.commit()
        conn.close()
        print(f"[INFO] Registered new file: {filename} with {len(chunk_data)} chunks.")
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

def get_file_directory():
    """Called by the Client to populate the Streamlit file browser."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Count how many chunks each file has
    cursor.execute("SELECT filename, COUNT(chunk_name) FROM file_chunks GROUP BY filename")
    files = cursor.fetchall()
    conn.close()
    
    # Format for the GUI
    registry = {}
    for filename, chunk_count in files:
         registry[filename] = f"{chunk_count} chunks stored"
    return registry

def get_chunk_locations(filename):
    """Called by the Client when downloading a file."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chunk_name, node_ip FROM file_chunks WHERE filename=?", (filename,))
    locations = cursor.fetchall()
    conn.close()
    return locations

def receive_heartbeat(node_address):
    """Catches the ping from the Data Nodes."""
    print(f"💓 Heartbeat received from Data Node at {node_address}")
    return True

# --- SERVER STARTUP ---
def start_master():
    init_db()
    
    # Set up the network server on port 5000
    server_address = ('0.0.0.0', 5000)
    server = xmlrpc.server.SimpleXMLRPCServer(server_address, allow_none=True)
    
    # Register the existing core functions
    server.register_function(register_file_chunks, "register_file_chunks")
    server.register_function(get_file_directory, "get_file_directory")
    server.register_function(get_chunk_locations, "get_chunk_locations")
    
    # ---> NEW: Register the heartbeat function <---
    server.register_function(receive_heartbeat, "receive_heartbeat")
    
    print("🧠 Master Node is running on port 5000...")
    print("Waiting for connections from Clients or Data Nodes...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMaster Node shutting down.")

if __name__ == "__main__":
    start_master()
