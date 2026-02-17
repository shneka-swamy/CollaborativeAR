import socket
import os
import argparse
import time
#import numpy as np

# For mininet
#HOST = '10.0.0.2'
HOST = '127.0.0.3'
PORT = 65432

def argparser():
    parser = argparse.ArgumentParser("Send images from the client to the server")
    parser.add_argument('--input_dir', help="Path to the image file")
    parser.add_argument('--file_name', help="File name for the images")
    return parser.parse_args()

def send_image(s, image_path):
    filename = os.path.basename(image_path)
    image_size = os.path.getsize(image_path)

    s.sendall(len(filename).to_bytes(4, 'big'))
    s.sendall(filename.encode('utf-8'))

    s.sendall(image_size.to_bytes(8, 'big'))

    with open(image_path, 'rb') as f:
        while True:
            bytes_read = f.read(4096)
            if not bytes_read:
                break
            s.sendall(bytes_read)
    
    ack = s.recv(2)
    print("Server ACK:", ack)
    print(f"Image '{filename}' sent successfully.")


def main():
    args = argparser()   
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))
        print(f"Connected to server on {HOST}:{PORT}")
        image_path = './dummy.png'       
        for i in range(10):
            send_image(s, image_path)
            time.sleep(1)

        # for _ in range(10):
        #     s.sendall(b"Hello from client")
        #     data = s.recv(1024)
        #     print(f"Received from server: {data.decode()}")
    print("Client all done")

if __name__ == '__main__':
    main()