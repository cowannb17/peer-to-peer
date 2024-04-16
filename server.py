# Code for server client of peer-to-peer system
import msvcrt
import socket
import threading

max_threads = 3

def accept_connection(conn, addr):
    print(f"Accepting connection from {addr}")
    with conn:
        # Sends data and recieves the uuid data from the client which can either be "first time user" or the uuid
        conn.sendall(b'secure_code')
        uuid_data = conn.recv(1024)
        
        # If the return message is blank end the connection
        if not uuid_data:
            conn.close()
            return
        
        # Checks to see if the user is either a first time user or that the uuid is sent with correct formatting
        if b'UUID: ' not in uuid_data and b'first time user' not in uuid_data:
            conn.close()
            return
        
        active_user = ""

        # If the user is a first time user, we create and send them their uuid and proceed with the resultant as the active user
        if b'first time user' in uuid_data:
            print("First time user")
            # Grant UUID to connector and create user
            uuid = "abc123"
            conn.send(uuid.encode()) # .encode creates a byte string, which is then sent
            active_user = uuid
        
        if b'UUID: ' in uuid_data:
            conn.send(b'verified')
            uuid = uuid_data[6:] # Removes "UUID: " part of string
            active_user = uuid

        # After opening sequence is finished, listens for many different types of incoming data
        while True:
            data = conn.recv(1024)

            # If there is no data in the message, end the connection
            if not data:
                break
            
            # If the incoming data is "down_list" send the downloads list to the client
            if data == b'down_list':
                conn.sendall(b'a.txt, b.mp4')

            # If the incoming data is "close_connection" end the connection to the client
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

    # Creates a thread to deal with the incoming connection
    thread = threading.Thread(target=accept_connection, args=(conn, addr,))
    thread.start()