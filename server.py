# Code for server client of peer-to-peer system
import rsa
from messageMethods import sendRsa, recieveRsa
import msvcrt
import socket
import threading
import uuid as UUID
from database import database

max_threads = 10

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

db_init = database()


def create_uuid():
    return str(UUID.uuid4())

def verify_user(db, uuid):
    data = db.select_data("Users", "uuid")
    result = any(uuid == value[0] for value in data) # Checks to see if the uuid is in the list of UUIDs
    return result

def add_user(db, uuid, pubkey):
    db.insert_data("Users", "'{}', '{}'".format(uuid, pubkey))

def add_file(db, filename, uuid):
    print(filename)
    db.insert_data("Files", "'{}', '{}'".format(filename, uuid))

def add_host(db, uuid, ip):
    db.insert_data("Hosts", "'{}', '{}'".format(uuid, ip))

def get_uuid_pubkey(db, uuid):
    data = db.execute_select("SELECT pubkey FROM Users WHERE UUID LIKE '{}'".format(uuid))[0][0]
    return data

def get_user_id(db, uuid):
    return db.select_data("Users", ["UUID"], f"UUID='{uuid}'")[0][0]


def get_file_list(db):
    #results = db.select_data("Files", "filename") # Gets all the filenames from the database
    results = db.execute_select("SELECT DISTINCT filename FROM Files") # Gets all the distinct filenames from the database
    filenames = [result[0] for result in results] # Converts the list of tuples to a list of strings
    filenames = str(filenames)[1:-1] # Removes the brackets from the string
    file_list = filenames.split(", ") # Creates a list of files from the file names
    file_list_sending_string = ':'.join([file.strip("'") for file in file_list]) # One liner to create a single string with files delimited by ":"
    return file_list_sending_string

def get_host_list(db, file_list):
    return_list = ""
    for file in file_list.split(":"):
        query = """
            SELECT Hosts.ip 
            FROM Hosts 
            INNER JOIN Files ON Hosts.host_uuid = Files.host_uuid 
            WHERE Files.filename = '{}'
        """.format(file)
        result = db.execute_select(query)
        print(result)
        host_list = [host[0] for host in result]
        host_list = str(host_list)[1:-1]
        host_list = host_list.split(", ") # Creates a list of files from the file names
        host_list = ':'.join([host.strip("'") for host in host_list]) # One liner to create a single string with files delimited by ":"
        return_list += host_list + "*" #Uses * as list delimeter
    return return_list[:-1]

def clear_all_files(db):
    """
    Clears the file list in the database.

    Parameters:
    - db: The database object used to execute the SQL query.

    Returns:
    None
    """
    db.execute_insert("DELETE FROM Files")
    
def clear_file_list(db, uuid):
    # Clear the file list for a specific user
    db.execute_insert(f"DELETE FROM Files WHERE host_uuid LIKE '{uuid}'")
    
def clear_all_hosts(db):
    """
    Clears the host list in the database.

    Parameters:
    - db: The database object used to execute the SQL query.

    Returns:
    None
    """
    db.execute_insert("DELETE FROM Hosts")
    
def clear_host_list(db, uuid):
    # Clear the host list for a specific user
    db.execute_insert(f"DELETE FROM Hosts WHERE host_uuid LIKE '{uuid}'")


def accept_connection(conn, addr):
    print(f"Accepting connection from {addr}")
    db = database()
    with conn:
        
        # Check if this is a first time user or a returning user
        msg = conn.recv(1024)
        # if client is the requsting to send their public key , then the client is a first time user
        if msg == b'public_key': #client wants to send public key
            # Send message to client requesting public key
            conn.sendall(b'send_public_key')
            # Recieve public key from client
            client_pubkey_pem = conn.recv(1024).decode('utf-8')
            client_pubkey = rsa.key.PublicKey.load_pkcs1(client_pubkey_pem)

            # send the server's public key to the client
            pubkey_pem = server_public_key.save_pkcs1().decode('utf-8')
            pubKeyString = f'{pubkey_pem}'
            conn.sendall(pubKeyString.encode())

            # Now that keys have been exchanged, send the client a UUID

            uuid_str = create_uuid()
            sendRsa(uuid_str, client_pubkey, conn) # Send UUID to client
            
            active_user = uuid_str
            add_user(db, uuid_str, client_pubkey_pem)

            recieveRsa(server_private_key, conn)


        # If the client is not a first time user, then the client is a returning user
        # The client will send their UUID to the server encrypted with the server's public key



        # Recieve UUID from client
        encrypted_uuid = msg

        if not encrypted_uuid:
            return
        
        # Decrypt the UUID with the server's private key
        if encrypted_uuid == b'public_key':
            return
        
        uuid = rsa.decrypt(encrypted_uuid, server_private_key)
        uuid = uuid.decode('utf-8')
        
        
        if uuid == "UUID_request":
            uuid_str = create_uuid()
            sendRsa(uuid_str, client_pubkey, conn) # Send UUID to client
            active_user = uuid_str
        elif "UUID:" in uuid:
            if not verify_user(db, uuid[5:]):
                #sendRsa("not_verified", client_pubkey, conn)
                conn.close()
                return
            else:
                client_pubkey = rsa.key.PublicKey.load_pkcs1(get_uuid_pubkey(db, uuid[5:]))
                sendRsa("verified", client_pubkey, conn)
                active_user = uuid[5:]
        else:
            #sendRsa("not_verified", client_pubkey, conn)
            conn.close()
            return

        

        # After opening sequence is finished, listens for many different types of incoming data
        while True:
            data = recieveRsa(server_private_key, conn)

            # If there is no data in the message, end the connection
            if not data:
                break
            
            # If the incoming data is "down_list" send the downloads list to the client
            if data == 'down_list':
                file_list = get_file_list(db)
                sendRsa(file_list, client_pubkey, conn) # Send file list to client
            # If the incoming data is "connection_data" send back the ip that the user is using
            if data == 'connection_data':
                ip = f"{addr[0]}"
                sendRsa(ip, client_pubkey, conn)

            # If the incoming data is "request_downloads" get the list of downloads requested and send the connection info of the files to the user
            #TODO: Implement this
            if data == 'request_file_hosts':
                download_data = recieveRsa(server_private_key, conn)
                # Send all users that offer the requested file to the user
                # Send the data as '127.0.0.1 for each user
                # Each file will have its own list as well e.g.
                # 127.0.0.1*127.0.0.1:127.0.0.1
                # Uses * as a delmiteter between lists and : as a delimiter within lists
                # File 1 has only a single host, file 2 has 2 hosts.
                packet = get_host_list(db, download_data)
                sendRsa(packet, client_pubkey, conn)

            # If the incoming data is "host_files" get the list of files the user wants to host
            if data == 'host_files':
                file_string = recieveRsa(server_private_key, conn)
                for file in file_string.split(":"):
                    #Add file to database list of included files
                    add_file(db, file, active_user)
                    #Add user to database list of current hosts
                    ip, port = addr
                    add_host(db, active_user, ip)
                
            if data == 'stop_hosting':
                # use active_user to clear the file list for the user
                clear_file_list(db, active_user)
                clear_host_list(db, active_user)
                
            
            # If the incoming data is "close_connection" end the connection to the client
            if data == 'close_connection':
                print(f"Closing connection from {addr}")
                conn.close()
                break

            #print(data)


# Allows for closing of socket while it is still listening, waits for 'Ctrl-C' press then closes socket
def await_keypress(sock):
    while True:
        if msvcrt.getch() == b'\x03': # If 'Ctrl-C' is pressed
            global open
            open = False
            sock.close()
            break

db_init.create_table("Users", "UUID, pubkey")
db_init.create_table("Files", "filename, host_uuid")
db_init.create_table("Hosts", "host_uuid, ip")

# Since server is starting fresh, clear the file and host lists
clear_all_files(db_init)
clear_all_hosts(db_init)

#add_file(db_init, "a.txt", 'none')  # Inserting some test data
#add_file(db_init, "b.txt", 'none')
#add_host(db_init, 'none', '127.0.1.1')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Opening Server at 0.0.0.0 on port 12756")
sock.bind(('0.0.0.0', 12756))
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
        conn.send(b'Connection Refused') # may need to be changed to sendRsa
        conn.close()
        continue
    
    # Creates a thread to deal with the incoming connection
    thread = threading.Thread(target=accept_connection, args=(conn, addr,))
    thread.start()