# Code for peer client of peer-to-peer system
import socket
import tkinter as tk

window = tk.Tk()
window.geometry("400x150")

frame = tk.Frame(window)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

downloads = [] # Each download is a dictionary of the filename and a boolean value of whether the user wants to download the file aka "checked"

def fetch_downloads():
    sock.send(b'down_list')
    data = sock.recv(1024)
    data = data.decode()

    for filename in data.split(", "):
        downloads.append( {"filename": filename, "checked": tk.BooleanVar()} ) # Creation of download dictionary
    
    print("Downloads Fetched")


def initialize_connection():
    try:
        sock.connect(('127.0.0.1', 12756))
        data = sock.recv(1024)
        if data == b'secure_code':
            print("Good to Go")
            fetch_downloads()
            return True
    except:
        sock.close()
        return False
    #sock.close()
    return False


def clearFrame():
    print("Clear")
    for widget in frame.winfo_children():
        widget.destroy()

def request_downloads():
    sort_by_checked = sorted(downloads, key=lambda file: file["checked"].get(), reverse=True)
    checked_downloads = []
    for file in sort_by_checked:
        if file["checked"].get() == False:
            break
        checked_downloads.append(file)

    print(checked_downloads)
    if (len(checked_downloads) == 0):
        return
    
    # send server the list files you want to download


def offered_files_frame():
    window.title('Peer Client: Offered Files')

    tk.Label(frame, text='Download Section').pack()
    download_list = tk.Frame(frame)
    for download in downloads:
        tk.Checkbutton(download_list, text=download["filename"], variable=download["checked"]).pack()
    download_list.pack(side="top", fill="x")
    
    tk.Button(frame, text='Download', command=request_downloads).pack()
    tk.Button(frame, text='Refresh', command=lambda:[fetch_downloads(), clearFrame(), offered_files_frame()]).pack()


def host_files_frame():
    window.title('Peer Client: File Hosting')
    tk.Label(frame, text='Hosting Section').pack()
    tk.Button(frame, text='Host the File').pack()


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


def root_window(connected):
    window.title('Peer Client')
    header = tk.Frame(window)
    header.pack(side="top", fill="x")
    tk.Button(header, text='See Downloadable Files', command=lambda:[clearFrame(), offered_files_frame()]).pack(side="left", expand="True")
    tk.Button(header, text='Host a file', command=lambda:[clearFrame(), host_files_frame()]).pack(side="left", expand="True")
    tk.Button(header, text='Settings', command=lambda:[clearFrame(), settings_frame()]).pack(side="left", expand="True")
    welcome_text = 'Welcome to the peer-to-peer file sharing application!'
    if not connected:
         welcome_text = 'Something went wrong when conncting to the server! Try again'      
    tk.Label(frame, text=welcome_text).pack()
    return window


init = initialize_connection()
w = root_window(init)
frame.pack(side="top", expand=True, fill="both")
w.mainloop()