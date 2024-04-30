import os
import rsa
import socket
import keyring
import threading
from user import user as User
from messageMethods import sendRsa, recieveRsa

class peer:
    def __init__(self, user : User):
        self.user = user

    def configure_hosting(self, files_to_host):
        self.hosted_files = files_to_host
        self.hosted_filenames = [file.split("/")[-1] for file in files_to_host]
        self.hosted_file_sizes = []
        for file in self.hosted_files:
            file_stats = os.stat(file)
            self.hosted_file_sizes.append(file_stats.st_size)


    def configure_downloads(self, requested_files, file_hosts):
        self.requestedFiles = requested_files
        self.hosts = file_hosts
        self.downloads = []

    
    def start_downloads(self):
        for index, file in enumerate(self.requestedFiles):
            ip = self.hosts[index]
            print(ip)
            print(file)
            self.start_download(ip, file)
            print("no")
            
            
            #try:
            #    while True:
            #        size = next(download)
            #        yield f"{file}:size:{size}"
            #        break
            #except StopIteration:
            #    return
            
            #try:
            #    while True:
            #        progression = next(download)
            #        yield progression
            #except StopIteration:
            #    return


    def request_from_ip(self, ip_list, files_to_download):
        for index, file in enumerate(files_to_download):
            ip = ip_list[index]
            self.start_download(self, ip, file)

    
    def start_download(self, ip, filename):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 13456))

        sock.send(self.to_bytes(self.get_RSA_pubkey().save_pkcs1().decode('utf-8')))
        peer_pubkey = rsa.key.PublicKey.load_pkcs1(self.to_string(sock.recv(1024)))
        print(peer_pubkey)
        
        if not peer_pubkey:
            sock.close()
            return
        
        print ("asking for size")
        sendRsa(f"request_file_size:{filename}", peer_pubkey, sock)
        response = recieveRsa(self.get_RSA_privkey(), sock)

        if not response:
            sock.close()
            return

        print(response)
        
        size = ""
        if "file_not_available" in response:
            sock.close()
            return
        else:
            size = response.split(":")[1]
            #yield size # Sends the file size to the parent function

        print("asking for file")
        sendRsa(f"request_file:{filename}", peer_pubkey, sock)
        response = recieveRsa(self.get_RSA_privkey(), sock)

        if not response:
            sock.close()
            return
        
        response = self.decode_message(response)
        if "file_not_available" in response:
            sock.close()
            return
        
        recieved_file = recieveRsa(self.get_RSA_privkey(), sock)
        
        # Gets path of current working directory of the script, and places the downloaded file there
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        abs_filename = f"{dirname}\\{filename}"
        with open(abs_filename, 'wb') as file:
            file.write(self.to_bytes(recieved_file))

        sock.send(self.encode_message('close_connection'))
        sock.close()
        return
        


    def send_file(self, conn, addr, file_index, peer_pubkey):
        path_to_file = self.hosted_files[file_index]
        file = open(path_to_file, 'rb')
        sendRsa(file.read(), peer_pubkey, conn)
        #try:
        #    while True:
        #        buffer = b''
        #        for _ in range(0, 1024):
        #            chunk = file.read(53) # Max number of bytes we can encrypt at a time with our key
        #            if not chunk:
        #                break
        #            buffer += self.encode_message(peer_pubkey, chunk)
        #        conn.sendall(buffer)
        #finally:
        #    file.close()
        #    conn.send(b"file_end")
        
    # Sends the file to the peer who has requested it
    def init_connection(self, conn, addr):
        print(f"Accepting connection from {addr}")
        with conn:
            peer_pubkey = conn.recv(1024)
            
            if not peer_pubkey:
                conn.close()
                return
            peer_pubkey = rsa.key.PublicKey.load_pkcs1(self.to_string(peer_pubkey))
            

            # Get personal pubkey and send as byte array
            personal_pubkey = self.get_RSA_pubkey()
            conn.sendall(self.to_bytes(personal_pubkey.save_pkcs1().decode('utf-8')))


            print("Keys exchanged")
            # Continues incoming connection until a valid 
            while True:
                # Get file request from user
                print("recieve")
                file_data = recieveRsa(self.get_RSA_privkey(), conn)
                print("data gotten")
                if not file_data:
                    conn.close()
                    return

                # Compares decoded message against "request_file and grabs the file the user is requesting"
                request = file_data
                if "request_file_size:" in request:
                    # Removes "request_file_size:" from the string
                    file = request[18:]
                    
                    index = self.hosted_filenames.index(file)
                    if index == -1:
                        sendRsa("file_not_available", peer_pubkey, conn)
                        conn.close()
                        return
                    print("asking size")
                    size = self.hosted_file_sizes[index]
                    file_and_size = f"{file}:{size}"
                    sendRsa(file_and_size, peer_pubkey, conn)
                    continue
                elif "request_file:" in request:
                    print("asking file")
                    file = request[13:]
                    
                    index = self.hosted_filenames.index(file)
                    if index == -1:
                        sendRsa("file_not_available", peer_pubkey, conn)
                        conn.close()
                        return
                    
                    sendRsa(f"sending_file:{file}", peer_pubkey, conn)

                    self.send_file(conn, addr, index, peer_pubkey)

                    continue
                elif request == "close_connection":
                    conn.close()
                    return
                else:
                    conn.close()
                    return
            
            # Send file and complete message once done sending
            return
            

    # Will act as server to host the files 
    def start_listen(self):
        # Start socket for hosting
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 13456))
        sock.listen()

        global open
        open = True
        # Start while loop for hosting
        while open:
            conn, addr = sock.accept() # conn = socket, addr = Ip address

            # If new request, make a new thread and being sending the data
            # - Send data
            # - Send "Complete" message once all data has been sent
            # - Close connection and thread
            thread = threading.Thread(target=self.init_connection, args=(conn, addr,))
            thread.start()
            
            
        return None

    # Turns a string into a byte string
    def to_bytes(self, message):
        return message.encode()
    
    # Encodes the message with the connected users public key
    # Remember NOT TO ENCRYPT WITH OWN PUBKEY, encrypt with peers pukey
    def encode_message(self, pubkey, message):
        return rsa.encrypt(message, pubkey)

    # Turns byte string into string
    def to_string(self, message):
        return message.decode("utf-8")

    # Decodes the message using our private key
    def decode_message(self, message):
        return self.to_string(rsa.decrypt(message, self.get_RSA_privkey()))

    # Saves public key to keyring
    def save_RSA_pubkey(self, pubkey):
        pubkey_pem = pubkey.save_pkcs1().encode('utf-8')
        keyring.set_password("p2p", "pubkey", pubkey_pem)

    # Saves private key to keyring
    def save_RSA_privkey(self, privkey):
        privkey_pem = privkey.save_pkcs1().encode('utf-8')
        keyring.set_password("p2p", "privkey", privkey_pem)

    # Gets public key from keyring
    def get_RSA_pubkey(self):
        key_string = keyring.get_password("p2p", "pubkey")
        return rsa.key.PublicKey.load_pkcs1(key_string)

    # Gets private key from keyring
    def get_RSA_privkey(self):
        key_string = keyring.get_password("p2p", "privkey")
        return rsa.key.PrivateKey.load_pkcs1(key_string)