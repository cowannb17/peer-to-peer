# Code for peer client of peer-to-peer system
import socket
import keyring
import tkinter as tk

window = tk.Tk()
window.geometry("400x150")

frame = tk.Frame(window)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

downloads = [] # Each download is a dictionary of the filename and a boolean value of whether the user wants to download the file aka "checked"

# Will encode the message with whatever encoding we decide on, currently only turns a string into a byte string
def encode_message(message):
    return message.encode()

# Will decode the message with whatever encoding we decide on, currently turns byte string into string
def decode_message(message):
    return message.decode("utf-8")

# Saves user id to keyring
def save_user_id(user_id):
    keyring.set_password("p2p", "uuid", user_id)

# Gets user id from keyring
def load_user_id():
    return keyring.get_password("p2p", "uuid")

# Connects to server, returns True if connection was successful, False if there were issues
def connect_to_server():
    try:
        # connects to server and recieves data
        sock.connect(('127.0.0.1', 12756))
        data = sock.recv(1024)
        
        # Decodes the incoming message and checks if it is equal to the secure code, in which case it continues
        if decode_message(data) != "secure_code":
            sock.close()
            return False
        
        # Gets user id and sends it to the server, if there is no user id it requests one from the server
        user_id = load_user_id()
        if user_id is None:
            # Sends message of no user id
            message = encode_message("first time user")
            sock.send(message)

            # Recieves user ID and saves it to the keyring
            uuid_data = sock.recv(1024)
            uuid = decode_message(uuid_data)
            save_user_id(uuid)
        else:
            # Sends message with the uuid to the server
            message = encode_message("UUID: {user_id}")
            sock.send(message)

            # Recieves verification, if not verified closes connection
            verification_data = sock.recv(1024)
            verification = decode_message(verification_data)
            if "verified" not in verification:
                print("Unverified")
                #sock.close()
                #return False
        
        return True
    except Exception as e:
        print(e)
        sock.close()
        return False

# Fetch downloads list from the server 
def fetch_downloads(*args):
    # If the socket is not connected, opens a connection to the server again
    if len(args) == 0 or args[0] != "socket connected":
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not connect_to_server():
            return False

    # Encodes and sends the message to request the downloads list
    message = encode_message("down_list")
    sock.send(message)

    # Receives data on all available downloads
    download_data = sock.recv(1024)
    downloads_list = decode_message(download_data)

    # Creates a dictionary of lists of download files and checkbox boolean variables to associate a file with a checkbox later on in the downloads GUI
    for filename in downloads_list.split(", "):
        downloads.append( {"filename": filename, "checked": tk.BooleanVar()} ) # Creation of download dictionary
    
    print("Downloads Fetched")
    sock.send(b'close_connection')
    sock.detach()
    return True


# Runs on program startup, connects to server and requests downloads, returns False if server connection failed, True if everything went well
def initialize_connection():
    if connect_to_server():
        fetch_downloads("socket connected")
        return True
    else:
        sock.close()
        return False


# Clears Tk window, needs to be run every time the window is changed
def clearFrame():
    for widget in frame.winfo_children():
        widget.destroy()


# Method to request all checked downloads from the server, grabs the list of downloads and sends the list of checked to the server
def request_downloads():
    # Gets list of downloads, sorts by whether they are checked or not
    # i.e. groups checked and unchecked downloads together
    sort_by_checked = sorted(downloads, key=lambda file: file["checked"].get(), reverse=True)

    # Adds checked downloads to list until it runs into the first unchecked download
    # at which point all checked downloads have been added to the list
    checked_downloads = []
    for file in sort_by_checked:
        if file["checked"].get() == False:
            break
        checked_downloads.append(file)

    # Checks to see if no downloads are checked at all
    if (len(checked_downloads) == 0):
        return
    
    # send server the list files you want to download


# Refreshes downloads list
def refresh_downloads():
    clearFrame()
    # resets downloads list
    global downloads
    downloads = []
    fetch_downloads()
    offered_files_frame()


# Static frame setup of the file download frame, called every time the "See Downloadable Files" button is clicked
def offered_files_frame():
    # Changes window title
    window.title('Peer Client: Offered Files')

    # Creates a text label above the downloads section
    tk.Label(frame, text='Download Section').pack()
    
    # Creates the downloads list section as a new frame, 
    download_list = tk.Frame(frame)
    for download in downloads:
        tk.Checkbutton(download_list, text=download["filename"], variable=download["checked"]).pack()
    # Add download list to the frame
    download_list.pack(side="top", fill="x")
    
    # Add download and refresh buttons to the frame, refresh button
    tk.Button(frame, text='Download', command=request_downloads).pack()
    tk.Button(frame, text='Refresh', command=refresh_downloads).pack()


# TODO: add file drag and drop or other selection style
#       add method to send files from computer to server
def host_files_frame():
    window.title('Peer Client: File Hosting')
    tk.Label(frame, text='Hosting Section').pack()
    tk.Button(frame, text='Host the File').pack()


# TODO: add saving of options
# Static frame setup of settings frame
def settings_frame():
    window.title('Peer Client: Settings')
    tk.Label(frame, text='Settings Section').pack()
    options = tk.Frame(frame)
    options.pack(side="top", fill="x", padx=40)
    
    tk.Label(options, text='Bandwidth used for Hosting: ', justify=tk.LEFT).grid(sticky=tk.E, row=0, column=0)
    up_bandwidth = tk.Entry(options, width=8)
    up_bandwidth.insert(0, 50)
    up_bandwidth.grid(sticky = tk.W, row = 0, column = 1)
    tk.Label(options, text='Mbps').grid(sticky=tk.W, row=0, column=2)
    
    tk.Label(options, text='Bandwidth used for Downloading: ', justify=tk.LEFT).grid(sticky=tk.E, row=1, column=0)
    down_bandwidth = tk.Entry(options, width=8)
    down_bandwidth.insert(0, 50)
    down_bandwidth.grid(sticky=tk.W, row=1, column=1)
    tk.Label(options, text='Mbps').grid(sticky=tk.W, row=1, column=2)

    tk.Button(options, text='Apply Settings').grid(sticky = tk.W+tk.E, row=3, column=0, columnspan=3)


# Static frame setup of root window, what the client first sees on program startup
def root_window(connected):
    window.title('Peer Client')
    # Creates header frame for all directory buttons
    header = tk.Frame(window)
    header.pack(side="top", fill="x")
    
    # Creates buttons for changing frames, note that the frame must be cleared before the new frame is rendered
    tk.Button(header, text='See Downloadable Files', command=lambda:[clearFrame(), offered_files_frame()]).pack(side="left", expand="True")
    tk.Button(header, text='Host a file', command=lambda:[clearFrame(), host_files_frame()]).pack(side="left", expand="True")
    tk.Button(header, text='Settings', command=lambda:[clearFrame(), settings_frame()]).pack(side="left", expand="True")
    
    # Adds welcome text that changes based on whether or not the program was able to connect to the server
    welcome_text = 'Welcome to the peer-to-peer file sharing application!'
    if not connected:
         welcome_text = 'Something went wrong when conncting to the server! Try again'      
    tk.Label(frame, text=welcome_text).pack()
    return window

# Connects to the server and then renders the window
init = initialize_connection()
w = root_window(init)
frame.pack(side="top", expand=True, fill="both")
w.mainloop()