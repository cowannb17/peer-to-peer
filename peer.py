import socket
import threading
from user import user as User

class peer:
    def __init__(self, user : User, isHosting, requested_files, file_hosts):
        self.requestedFiles = requested_files
        self.hosts = file_hosts
        self.downloads = []
        self.hosting = isHosting


    # Given a user and file (or list of files) connects to the user and requests the files. If the user has the files, start the download, if not do nothing
    def request_from_user(self, user : User, file_id):
        if type(file_id) is list:
            for file in file_id:
                self.request_from_user(user, file)
            return None
        
        return None


    # Starts the download by requesting the download data of the file (file size in bytes)
    def start_download(self, user : User, file_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((user.userIP, 12756))
        sock.send(b'get_download_data')
        sock.send(file_id)

    # Sends the file to the peer who has requested it
    def send_file(self, conn, addr, file_id):
        print(f"Accepting connection from {addr}")
        with conn:
            download_data = conn.recv(1024)
            if not download_data:
                conn.close()
                return
            
            if download_data != b'get_download_data':
                conn.close()
                return
            
            # Send file and complete message once done sending
            return
            

    # Will act as server to hsot only the singular file, multiple threads for each file and each thread will create threads for incoming connections
    def host_download(self, file_id):
        # Parse file into global memory
        
        # Start socket for hosting
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 12756))
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
            thread = threading.Thread(target=self.send_file, args=(conn, addr, file_id,))
            thread.start()
            
            
        return None