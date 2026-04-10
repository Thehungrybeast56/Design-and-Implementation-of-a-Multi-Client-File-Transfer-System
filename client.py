import socket
import os

PORT = 5001
BUFFER_SIZE = 4096


def run_client(ip_address, file_to_send):
    if not os.path.exists(file_to_send):
        print(f"File {file_to_send} not found!")
        return

    filesize = os.path.getsize(file_to_send)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((ip_address, PORT))
        print(f"[CONNECT] Connected to server {ip_address}:{PORT}")

        filename = os.path.basename(file_to_send)
        header = f"{filename}|{filesize}\n".encode()
        client.sendall(header)
        print(f"[SENDING] {filename} ({filesize} bytes)")

        with open(file_to_send, "rb") as f:
            while (data := f.read(BUFFER_SIZE)):
                client.sendall(data)

        print("[SUCCESS] File sent successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    target_ip = input("Enter Server IP (default 127.0.0.1): ") or "127.0.0.1"
    fname = input("Enter filename to send: ").strip()
    if fname:
        run_client(target_ip, fname)
    else:
        print("No filename entered. Exiting.")
