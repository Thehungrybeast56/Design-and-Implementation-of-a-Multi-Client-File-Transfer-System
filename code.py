import socket
import threading
import os
import sys

# Shared Constants [cite: 25, 26, 50]
PORT = 5001
BUFFER_SIZE = 4096

# --- SERVER LOGIC ---
def handle_client(conn, addr):
    """Handles the concurrent file transfer for a single client[cite: 5, 68]."""
    print(f"[CONNECTED] {addr}")
    try:
        # Step 1: Receive Metadata [cite: 99]
        header = b""
        while b"\n" not in header:
            chunk = conn.recv(1024)
            if not chunk:
                raise ConnectionError("Client disconnected before sending metadata")
            header += chunk

        header, remaining_data = header.split(b"\n", 1)
        filename, filesize_str = header.decode().split("|", 1)
        filesize = int(filesize_str)
        print(f"[RECEIVING] {filename} ({filesize} bytes) from {addr}")
        
        # Step 2: Receive File Chunks [cite: 6, 100]
        with open(f"received_{filename}", "wb") as f:
            if remaining_data:
                f.write(remaining_data)
                remaining = filesize - len(remaining_data)
            else:
                remaining = filesize

            while remaining > 0:
                data = conn.recv(min(remaining, BUFFER_SIZE))
                if not data:
                    break
                f.write(data)
                remaining -= len(data)
        print(f"[SUCCESS] Received {filename} from {addr}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def run_server():
    """Initializes the central server to listen for connections[cite: 23, 67]."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    print(f"[LISTENING] Server is active on port {PORT}...")
    
    while True:
        conn, addr = server.accept()
        # Multithreading allows handling multiple clients at once [cite: 5, 88]
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

# --- CLIENT LOGIC ---
def run_client(ip_address, file_to_send):
    """Connects to the server and transmits the file[cite: 49, 98]."""
    if not os.path.exists(file_to_send):
        print(f"File {file_to_send} not found!")
        return

    filesize = os.path.getsize(file_to_send)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((ip_address, PORT))
        print(f"[CONNECT] Connected to server {ip_address}:{PORT}")
        # Send filename and size metadata first [cite: 99]
        filename = os.path.basename(file_to_send)
        header = f"{filename}|{filesize}\n".encode()
        client.sendall(header)
        print(f"[SENDING] {filename} ({filesize} bytes)")
        
        # Send data in fixed-size chunks [cite: 101]
        with open(file_to_send, "rb") as f:
            while (data := f.read(BUFFER_SIZE)):
                client.sendall(data)
        print("[SUCCESS] File sent successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

print("Use server.py to start the server or client.py to send files.")
print("Example: python server.py")
print("Example: python client.py")
