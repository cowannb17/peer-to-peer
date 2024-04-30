# Code for server client of peer-to-peer system
import rsa
import msvcrt
import socket
import threading
import uuid as UUID
from database import database

max_threads = 3

def checkKeys():
    # Check if the keys are already generated
    try:
        with open('server_private.pem', 'rb') as file:
            private_key = rsa.PrivateKey.load_pkcs1(file.read())
        with open('server_public.pem', 'rb') as file:
            public_key = rsa.PublicKey.load_pkcs1(file.read())
    except FileNotFoundError:
        # Generate a new key pair
        (public_key, private_key) = rsa.newkeys(512)
        with open('server_private.pem', 'wb') as file:
            file.write(private_key.save_pkcs1())
        with open('server_public.pem', 'wb') as file:
            file.write(public_key.save_pkcs1())
    return public_key, private_key

server_public_key, server_private_key = checkKeys()

db = database()

def create_uuid():
    return str(UUID.uuid4())

def verify_user(uuid):
    return db.select_data("Users", ["UUID"], f"UUID='{uuid}'")[0][0] == uuid

def add_user(uuid, pubkey):
    db.insert_data("Users", (uuid, pubkey))

def get_user_id(uuid):
    return db.select_data("Users", ["uuid"], f"UUID='{uuid}'")[0][0]

def add_file(filename, uuid):
    db.insert_data("Files", (filename, uuid))

def get_file_list():
    result = db.select_data("Files", ["DISTINCT filename"], "")
    distinct_files = [row[0] for row in result]
    return distinct_files

def add_host(uuid, ip):
    db.insert_data("Hosts", (uuid, ip))

def accept_connection(conn, addr):
    print(f"Accepting connection from {addr}")
    with conn:
        
        # Check if this is a first time user or a returning user
        msg = conn.recv(1024)
        # if client is the requsting to send their public key , then the client is a first time user
        if msg == b'public_key': #client wants to send public key
            # Send message to client requesting public key
            conn.sendall(b'send_public_key')
            # Recieve public key from client
            client_pubkey = conn.recv(1024).decode('utf-8')
            
            # send the server's public key to the client
            pubKeyString = f'{server_public_key}'
            conn.sendall(pubKeyString.encode())

            # TODO: Assign UUID to the client
            uuid_str = create_uuid()
            uuid_message = rsa.encrypt(uuid_str, client_pubkey)
            conn.send(uuid_message) # .encode creates a byte string, which is then sent
            active_user = uuid_str
            add_user(uuid_str, client_pubkey)

            # Listen for encrypted uuid to arrive
            msg = conn.recv(1024)


        # If the client is not a first time user, then the client is a returning user
        # The client will send their UUID to the server encrypted with the server's public key
        if not msg:
            conn.close()
            return


        # Recieve UUID from client
        encrypted_uuid = msg
        
        # Decrypt the UUID with the server's private key
        uuid = rsa.decrypt(encrypted_uuid, server_public_key)
        uuid = uuid.decode('utf-8')
        if uuid == "UUID_request":
            uuid_str = create_uuid()
            uuid_message = rsa.encrypt(uuid_str, client_pubkey)
            conn.send(uuid_message) # .encode creates a byte string, which is then sent
            active_user = uuid_str
        elif "UUID:" in uuid:
            if not verify_user(uuid[5:]):
                conn.send("not_verified")
                conn.close()
                return
            else:
                conn.send("verified")
                active_user = uuid[5:]
        else:
            conn.send("not_verified")
            conn.close()
            return

        

        # After opening sequence is finished, listens for many different types of incoming data
        while True:
            data = conn.recv(1024)

            # If there is no data in the message, end the connection
            if not data:
                break
            
            # If the incoming data is "down_list" send the downloads list to the client
            if data == b'down_list':
                file_list = get_file_list()
                print(file_list)
                conn.send("abc.txt")

            # If the incoming data is "connection_data" send back the ip that the user is using
            if data == b'connection_data':
                ip = f"{addr[0]}"
                conn.sendall(ip.encode())

            # If the incoming data is "request_downloads" get the list of downloads requested and send the connection info of the files to the user
            if data == b'request_downloads':
                download_data = conn.recv(1024)
                print(download_data)
                # Send all users that offer the requested file to the user
                # Send the data as ('127.0.0.1', 12345) for each user
                # Each file will have its own list as well e.g.
                # [('127.0.0.1', 12345)],[('127.0.0.1', 12345),('127.0.0.1', 12345)]
                # File 1 has only a single host, file 2 has 2 hosts.
                packet = ''

                download_data = download_data.decode("utf-8")
                for i in range(0, len(download_data.split(","))):
                    packet += '[(\'127.0.0.1\', 12756)],'

                packet = packet[:-1]
                packet = "[(\'1.2.3.4\', 12345)],[(\'5.6.7.8\', 61234), (\'9.0.1.2\', 56789)]"
                conn.send(packet.encode())

            # If the incoming data is "host_files" get the list of files the user wants to host
            if data == b'host_files':
                file_string = conn.recv(1024)
                # add files to the database
                print(file_string)

            # If the incoming data is "close_connection" end the connection to the client
            if data == b'close_connection':
                print(f"Closing connection from {addr}")
                conn.close()
                break

            print(data)


# Allows for closing of socket while it is still listening, waits for 'Ctrl-C' press then closes socket
def await_keypress(sock):
    while True:
        if msvcrt.getch() == b'\x03': # If 'Ctrl-C' is pressed
            global open
            open = False
            sock.close()
            break

db.create_table("Users", "UUID TEXT PRIMARY KEY, pubkey TEXT")
db.create_table("Files", "filename TEXT, host_uuid TEXT PRIMARY KEY")
db.create_table("Hosts", "host_uuid TEXT PRIMARY KEY, ip TEXT")

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