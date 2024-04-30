import gc
import socket

import rsa
from RSAKeyExchange import RSAKeyExchange
import keyring
import tkinter as tk
from user import user as User

class client:
    
    class ClientConnection:
        def __init__(self):
            """
            Initializes a ClientConnection object.

            This method creates a socket object for the client and performs a key exchange with the server.
            It generates a new RSA key pair if the server's public key is not available, and saves the client's
            public and private keys to files. It then sends the client's public key to the server and receives
            the server's public key in return.

            Note: The key pair is deleted from memory after the key exchange to prevent it from being accessed
            by other programs.

            Args:
                None

            Returns:
                None
            """
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            if self.get_server_RSA_pubkey() is None:
                self.keyPair = RSAKeyExchange()
                
                self.save_RSA_pubkey(self.keyPair.get_public_key())
                self.save_RSA_privkey(self.keyPair.get_private_key())
                # Delete the keypair from memory to prevent it from being accessed by other programs
                self.keyPair = None
                gc.collect()

                # Key exchange between client and server
                self.sock.connect(('127.0.0.1', 12756))

                # Let server know you want to send your public key
                self.sock.send(self.encode_message("public_key"))

                msg = self.sock.recv(1024)

                if msg == b'send_public_key':
                    # Encode clients public key and send it to the server
                    self.sock.send(self.encode_message(self.get_RSA_pubkey()))
                    # Recieve Server's public key and decode from server
                    self.save_server_RSA_pubkey(self.decode_message(self.sock.recv(1024)))
                else :
                    print("Error in key exchange")
                    self.sock.close()
                    return

                # now the client has the server's public key, and the server has the client's public key
                # the client can now send the server a message encrypted with the server's public key
                # and the server can decrypt it with its private key
            else:
                self.sock.connect(('127.0.0.1', 12756))
                encoded_userID = self.encode_message(self.load_user_id())
                # Encrypt the message with the server's public key
                encrypted_userID = rsa.encrypt(encoded_userID, self.get_server_RSA_pubkey())
                self.sock.send(encrypted_userID)

                msg = self.sock.recv(1024)
                decrypted_msg = rsa.decrypt(msg, self.get_RSA_privkey())
                if decrypted_msg == b'UUID_recived':
                    print("UUID Recived by server")
                else:
                    print("Error in UUID exchange")
                    self.sock.close()
                    return

        


    # Will encode the message with whatever encoding we decide on, currently only turns a string into a byte string
    def encode_message(self, message):
        return message.encode()

    # Will decode the message with whatever encoding we decide on, currently turns byte string into string
    def decode_message(self, message):
        return message.decode("utf-8")

    # Saves user id to keyring
    def save_user_id(self, user_id):
        keyring.set_password("p2p", "uuid", user_id)

    # Gets user id from keyring
    def load_user_id(self):
        return keyring.get_password("p2p", "uuid")

    # Saves public key to keyring
    def save_RSA_pubkey(self, pubkey):
        keyring.set_password("p2p", "pubkey", pubkey)

    # Saves private key to keyring
    def save_RSA_privkey(self, privkey):
        keyring.set_password("p2p", "privkey", privkey)

    # Gets public key from keyring
    def get_RSA_pubkey(self):
        return keyring.get_password("p2p", "pubkey")

    # Gets private key from keyring
    def get_RSA_privkey(self):
        return keyring.get_password("p2p", "privkey")
    
    # Saves server public key to keyring
    def save_server_RSA_pubkey(self, pubkey):
        keyring.set_password("p2p", "server_pubkey", pubkey)

    # Gets server public key from keyring
    def get_server_RSA_pubkey(self):
        return keyring.get_password("p2p", "server_pubkey")

    # Private Method:
    # Connects to server, returns True if connection was successful, False if there were issues
    def __connect_to_server(self):

        if self.load_user_id() is None:
            self.keyExchange()
        try:
            # connects to server and recieves data
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 12756))
            data = self.sock.recv(1024)

            
            # Decodes the incoming message and checks if it is equal to the secure code, in which case it continues
            if self.decode_message(data) != "secure_code":
                self.sock.close()
                return False
            
            # Gets user id and sends it to the server, if there is no user id it requests one from the server
            user_id = self.load_user_id()
            if user_id is None:
                # Sends message of no user id
                message = self.encode_message("first time user") #Encodes as byte string
                self.sock.send(message)

                # Recieves user ID and saves it to the keyring
                uuid_data = self.sock.recv(1024)
                uuid = self.decode_message(uuid_data)
                self.save_user_id(uuid)
            else:
                # Sends message with the uuid to the server
                message = self.encode_message("UUID:{user_id}")
                self.sock.send(message)

                # Recieves verification, if not verified closes connection
                verification_data = self.sock.recv(1024)
                verification = self.decode_message(verification_data)
                if "verified" not in verification:
                    #print("Unverified")
                    #self.sock.close()
                    return False
            
            return True
        except Exception as e:
            print(e)
            self.sock.close()
            return False
    
    
        
        


    def __request_connection_data(self):
        self.sock.send(self.encode_message("connection_data"))
        data = self.sock.recv(1024)
        if not data:
            return
        return self.decode_message(data)

    # Connects to the server for the first time, then closes the connection
    def first_connection(self):
        status = self.__connect_to_server()
        self.user = User(self.load_user_id(), self.__request_connection_data())
        self.sock.send(b'close_connection')
        self.sock.detach()
        return status

    # Fetch downloads list from the server 
    def fetch_downloads_list(self):
        # Connects to server, if failure in connecting returns None
        if not self.__connect_to_server():
            return None
        
        # Encodes and sends the message to request the downloads list
        message = self.encode_message("down_list")
        self.sock.send(message)

        # Receives data on all available downloads
        download_data = self.sock.recv(1024)
        downloads_list = self.decode_message(download_data)

        downloads = []
        # Creates a dictionary of lists of download files and checkbox boolean variables to associate a file with a checkbox later on in the downloads GUI
        for filename in downloads_list.split(", "):
            downloads.append( {"filename": filename, "checked": tk.BooleanVar()} ) # Creation of download dictionary
        
        print("Downloads Fetched")
        self.sock.send(b'close_connection')
        self.sock.detach()
        return downloads
    
    
    # Requests a list of hosts for the list of files given to the server, takes in a comma seperated string of downloads
    def get_download_users(self, download_request_list):
        status = self.__connect_to_server()
        
        # If the connection to the server fails, return None
        if not status:
            return None
        
        # send server list of files the client wants to download
        message = self.encode_message("request_downloads")
        self.sock.send(message)
        self.sock.send(self.encode_message(download_request_list))

        # Recieves list of users who will host the requested file(s)
        data = self.sock.recv(1024)
        if not data:
            return None

        self.sock.send(b'close_connection')
        self.sock.detach()
        return self.decode_message(data)
    
    
    def notify_of_hosting(self, files_to_host):
        # Get the actual name of each file
        file_names = [file.split("/")[-1] for file in files_to_host]
        #one liner to add double quotes around each file name and put them in a single string
        files = ','.join(['"' + file_name + '"' for file_name in file_names])
        message = self.encode_message(files)
        
        # Connects to server
        status = self.__connect_to_server()
        if not status:
            return

        # Sends server list of files client wants to host
        self.sock.send(self.encode_message("host_files"))        
        self.sock.send(message)
        
        # Disconnects from server
        self.sock.send(b'close_connection')
        self.sock.detach()
