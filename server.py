# Code for server client of peer-to-peer system
import socket
import threading

def accept_connection(sock):
    conn, addr = sock.accept()
    print(f"Accepting connection from {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
        conn.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopot(socket.SOL_SOCKET, socket.SO_REUSERADDR, 1)
sock.bind(('0.0.0.0', 12756))
sock.listen()

accept_connection(sock)