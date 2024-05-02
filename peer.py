import os
import rsa
import socket
import keyring
import threading
from math import floor
from user import user as User
from messageMethods import sendRsa, recieveRsa, recieveFileRsa

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
            print("Getting file {} from host {}".format(file, ip))
            download_progress = self.start_download(ip, file)
            
            yield file

            for percentage in download_progress:
                
                if percentage == "end":
                    yield 100
                    break
                yield int(percentage)
        return 


    def request_from_ip(self, ip_list, files_to_download):
        for index, file in enumerate(files_to_download):
            ip = ip_list[index]
            self.start_download(self, ip, file)

    
    def start_download(self, ip, filename):
        # Initializes socket connecting to the host peer
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 13456))

        # Sends the client peers RSA public key to the host peer
        sock.send(self.to_bytes(self.get_RSA_pubkey().save_pkcs1().decode('utf-8')))
        # Receives host peer public key and creates a public key object
        peer_pubkey = rsa.key.PublicKey.load_pkcs1(self.to_string(sock.recv(1024)))
        
        # If no pubkey received, end the connection
        if not peer_pubkey:
            print("CLIENT: Pubkey not received")
            sock.close()
            return
        
        # Asks the host peer for the size of the file given by filename
        sendRsa(f"request_file_size:{filename}", peer_pubkey, sock)
        # Receives the filename from the host peer
        response = recieveRsa(self.get_RSA_privkey(), sock)

        # If no file size received, end the connection
        if not response:
            print("CLIENT: File size not received")
            sock.close()
            return

        # File not found on host, ending connection
        if "file_not_available" in response:
            print("CLIENT: File not found on host when requesting size, ending connection")
            sock.close()
            return


        recieved_filename, size = response.split(":")
        # Changes data size to size it will be when it is encrypted
        # ends up as a rough estimate but it is good enough for what we are doing
        encrypted_size = int(int(size) * 64 / 53)

        # Asks the host peer for the file set by filename
        sendRsa(f"request_file:{filename}", peer_pubkey, sock)
        # Recieves a confirmation from the host peer that we are downloading the correct file or that the file does not exist
        response = recieveRsa(self.get_RSA_privkey(), sock)

        # If response was empty, end the connection
        if not response:
            print("CLIENT: No data received from host peer")
            sock.close()
            return
        
        # If the file is not found on the host, end the connection
        if "file_not_available" in response:
            print("CLIENT: File not found on host when requesting file, ending connection")
            sock.close()
            return
        
        # Recieve the file from the host peer and write the decrypted data into the recieved_file variable
        recieved_file = recieveFileRsa(self.get_RSA_privkey(), sock)

        # Gets number of recieved bytes from the recieveFileRsa function and gives how far along the download is (percentage wise) to the parent function
        total_recieved_bytes = 0
        decrypted_recieved_file = ""
        for chunksize in recieved_file:
            if chunksize == "end":
                # Once the stream of chunk lengths has ended, recieve the actual file data
                decrypted_recieved_file = next(recieved_file)
                break
            elif int(chunksize) == 0:
                continue
            
            total_recieved_bytes += int(chunksize)
            
            yield floor(int(total_recieved_bytes) / int(encrypted_size) * 100) # Sends data upwards, like return but does not stop the method

        recieved_file = decrypted_recieved_file

        # If the response was empty, end the connectiom
        if not recieved_file:
            print("CLIENT: No data received from host peer when receiving file")
            return

        # Gets path of current working directory of the script, and creates the downloaded file there
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        abs_filename = f"{dirname}\\{filename}" # adds filename to the path

        # Creates file at abs_filename path and writes it as bytes to completion
        with open(abs_filename, 'wb') as file:
            file.write(recieved_file)

        yield "end"
        return True
        


    def send_file(self, conn, addr, file_index, peer_pubkey): # addr is not used
        # Gets correct path to the file we are sending
        path_to_file = self.hosted_files[file_index]
        
        # Reads the file and sends it to the client peer
        with open(path_to_file, 'rb') as file:
            file_bytes = file.read()
            bits = b'abc123'
            sendRsa(file_bytes, peer_pubkey, conn)

        conn.close()
        
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


            print("HOST: Keys exchanged")
            # Continues incoming connection until a valid 
            while True:
                # Get file request from user
                file_data = recieveRsa(self.get_RSA_privkey(), conn)
                
                # Checks to see that data was recieved
                if not file_data:
                    print("HOST: No data gotten from file_data")
                    conn.close()
                    return

                # Compares decoded message against "request_file and grabs the file the user is requesting"
                request = file_data
                if "request_file_size:" in request:
                    # Removes "request_file_size:" from the string
                    file = request[18:]
                    
                    # Gets index of file to use for all lists
                    index = self.hosted_filenames.index(file)

                    if index == -1:
                        print("HOST: File not found in request file size, index -1")
                        sendRsa("file_not_available", peer_pubkey, conn)
                        conn.close()
                        return

                    # Gets size in bytes of the file and sends that data to the peer
                    size = self.hosted_file_sizes[index]
                    file_and_size = f"{file}:{size}"

                    sendRsa(file_and_size, peer_pubkey, conn)
                    continue
                
                elif "request_file:" in request:
                    # Removes "request_file:" from the string
                    file = request[13:]
                    
                    # Gets index of file to use for all lists
                    index = self.hosted_filenames.index(file)

                    if index == -1:
                        print("HOST: file not found in request file, index -1")
                        sendRsa("file_not_available", peer_pubkey, conn)
                        conn.close()
                        return
                    
                    # Notifies peer on which file is being sent
                    sendRsa(f"sending_file:{file}", peer_pubkey, conn)

                    # Sends file
                    self.send_file(conn, addr, index, peer_pubkey)

                    # File is sent, no need for the thread anymore
                    break
                elif request == "close_connection":
                    print(f"Closing connection from {addr}")
                    conn.close()
                    return
                else:
                    print("HOST: Unrecognized Message")
                    conn.close()
                    return
            
            # Send file and complete message once done sending
            return
            

    # Will act as server to host the files 
    def start_listen(self):
        # Start socket for hosting
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 13456))
        sock.listen()

        global open_sockets
        open_sockets = True
        # Start while loop for hosting
        while open_sockets:
            conn, addr = sock.accept() # conn = socket, addr = Ip address
            print(f"Incoming connection from {addr}")

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
    # Turns byte string into string
    def to_string(self, message):
        return message.decode("utf-8")
        
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