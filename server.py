import socket
import threading

PORT = 5001
BUFFER_SIZE = 4096


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    try:
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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    print(f"[LISTENING] Server is active on port {PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    run_server()
