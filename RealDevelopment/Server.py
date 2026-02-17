import socket
import os

#HOST = '0.0.0.0' 
HOST = '127.0.0.3'
PORT = 65432      

def receive_image(conn, count):
    try:
        filename_len_bytes = conn.recv(4)
    except (ConnectionError, BrokenPipeError, OSError) as E:
        return False

    filename_len = int.from_bytes(filename_len_bytes, 'big')
    if filename_len <= 0 or filename_len > 4096:
        raise ValueError(f"unreasonable filename length: {filename_len}")

    filename = conn.recv(filename_len).decode('utf-8')
    if filename is None: 
        raise ConnectionError("closed while reading filename")
    image_size_bytes = conn.recv(8)
    if image_size_bytes is None: 
        raise ConnectionError("closed while reading file size")
    
    image_size = int.from_bytes(image_size_bytes, 'big')

    with open(f"received_{filename[:-4]}_{count}{filename[-4:]}", 'wb') as f:
        bytes_received = 0
        while bytes_received < image_size:
            chunk = conn.recv(4096)
            if not chunk:
                raise ConnectionError(
                    f"closed while receiving body "
                )
            f.write(chunk)
            bytes_received += len(chunk)
    print(f"Image '{filename}' received successfully and saved as received_{filename[:-4]}_{count}{filename[-4:]}")

    return True

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            count = 0
            with conn:
                while True:
                    got = receive_image(conn, count)
                    if not got:
                        print("[SERVER] Client closed (no more files).")
                        break
                    if got:
                        conn.sendall(b"Server received your image")
                        count += 1
            break
    print("[SERVER] Shutting down cleanly.")  
if __name__ == '__main__':
    main()