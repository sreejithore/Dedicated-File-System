import streamlit as st
import time
from client_logic import split_file, stitch_file

# --- INITIALIZE SESSION STATE ---
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'file_registry' not in st.session_state:
    # Mocking the Master Node's database
    st.session_state['file_registry'] = {} 

st.set_page_config(page_title="DFS Client Gateway", layout="wide")
st.title("Distributed File System Dashboard")

# --- 1. SIDEBAR: System Control & Status ---
with st.sidebar:
    st.header("System Connection")
    # Input boxes for the IP and Port of your Master Node [cite: 104]
    master_ip = st.text_input("Master Node IP", "127.0.0.1")
    master_port = st.text_input("Port", "5000")
    
    # A button to establish the initial connection [cite: 105]
    if st.button("Connect"):
        st.session_state['connected'] = True
        st.success(f"Connected to Master at {master_ip}:{master_port}!")
    
    if st.session_state['connected']:
        st.success("🟢 System Status: ONLINE")
    else:
        st.error("🔴 System Status: OFFLINE")

# --- 2. MAIN DASHBOARD: User Actions ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload a File")
    # Use st.file_uploader() [cite: 107]
    uploaded_file = st.file_uploader("Choose a file to upload to DFS")

    if uploaded_file is not None and st.session_state['connected']:
        if st.button("Upload to DFS"):
            # The "Behind the Scenes" Console 
            with st.status("Processing Upload...", expanded=True) as status:
                st.write("1. Reading file into memory...")
                file_bytes = uploaded_file.getvalue()
                
                st.write(f"2. Splitting '{uploaded_file.name}' into 2MB chunks...")
                # Call our logic function
                chunk_names = split_file(file_bytes, uploaded_file.name)
                time.sleep(1) # Simulating network delay
                
                st.write("3. Contacting Master for node addresses...")
                # Mocking the Master Node [cite: 134]
                st.session_state['file_registry'][uploaded_file.name] = chunk_names
                
                st.write(f"4. Sending {len(chunk_names)} chunks to Data Nodes...")
                
                status.update(label="Upload Complete!", state="complete", expanded=False)
                st.success(f"{uploaded_file.name} successfully chunked and stored!")

with col2:
    st.subheader("Files in DFS")
    
    # Display files currently stored [cite: 108]
    if st.session_state['file_registry']:
        for filename, chunks in st.session_state['file_registry'].items():
            st.markdown(f"**📄 {filename}** ({len(chunks)} chunks)")
            
            # Action button to download [cite: 109]
            if st.button(f"Download {filename}"):
                with st.spinner("Stitching chunks back together..."):
                    success, path = stitch_file(filename, chunks)
                    time.sleep(1) # Simulate download time
                    if success:
                        st.success(f"File downloaded successfully to your project folder as: {path}")
                    else:
                        st.error(path)
    else:
        st.info("No files currently in the system.")
