# Code for server client of peer-to-peer system
import socket
import threading

def accept_connection(sock):
    conn, addr = sock.accept() # conn = socket, addr = Ip address
    print(f"Accepting connection from {addr}")
    with conn:
        conn.sendall(b'secure_code')
        uuid_data = conn.recv(1024)
        if not uuid_data:
            conn.close()
            return
        if b'UUID: ' not in uuid_data and b'first time user' not in uuid_data:
            conn.close()
            return
        if b'first time user' in uuid_data:
            print("First time user")
            # Grant UUID to connector and create user
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data == b'down_list':
                conn.sendall(b'a.txt, b.mp4')
            if data == b'close_connection':
                conn.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Opening Server at 127.0.0.1 on port 12756")
sock.bind(('127.0.0.1', 12756))
sock.listen()

accept_connection(sock)