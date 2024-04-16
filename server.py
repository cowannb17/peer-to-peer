# Code for server client of peer-to-peer system
import msvcrt
import socket
import threading

max_threads = 3

def accept_connection(conn, addr):
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
            conn.send(b'abc123')
            # Grant UUID to connector and create user
        
        if b'UUID: ' in uuid_data:
            conn.send(b'verified')

        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data == b'down_list':
                conn.sendall(b'a.txt, b.mp4')
            if data == b'close_connection':
                conn.close()
                break


# Allows for closing of socket while it is still listening, waits for 'Ctrl-C' press then closes socket
def await_keypress(sock):
    while True:
        if msvcrt.getch() == b'\x03': # If 'Ctrl-C' is pressed
            global open
            open = False
            sock.close()
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Opening Server at 127.0.0.1 on port 12756")
sock.bind(('127.0.0.1', 12756))
sock.listen()

global open
open = True

# Opens a thread which waits for 'Control-C' to be pressed, then closes the socket.
# A thread is needed for this because sock.accept() is blocking
keyboard_interrupt_thread = threading.Thread(target=await_keypress, args=(sock,))
keyboard_interrupt_thread.daemon = True
keyboard_interrupt_thread.start()

while open:
    conn, addr = sock.accept() # conn = socket, addr = Ip address
    print(f"Incoming connection from {addr}")
    
    # If theads are at max, send a response "Connection Refused"
    if threading.active_count() > max_threads: # Active count includes main thread, so must use > rather than >=
        conn.send(b'Connection Refused')
        conn.close()
        continue

    # Creates a thread to deal with the incomic connection
    thread = threading.Thread(target=accept_connection, args=(conn, addr,))
    thread.start()