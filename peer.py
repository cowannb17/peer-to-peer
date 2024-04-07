# Code for peer client of peer-to-peer system
import socket
import tkinter as tk

window = tk.Tk()
window.geometry("400x150")

frame = tk.Frame(window)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def initialize_connection():
    try:
        sock.connect(('127.0.0.1', 12756))
        data = sock.recv(1024)
        if data == b'secure_code':
            print("Good to Go")
            return True
    except:
        sock.close()
        return False
    sock.close()
    return False

def clearFrame():
    for widget in frame.winfo_children():
        widget.destroy()

def offered_files_frame():
    sock.send(b'down_list')
    data = sock.recv(1024)
    data = data.decode()
    print(data)
    window.title('Peer Client: Offered Files')
    download_list = tk.Frame(frame)
    download_checked = []
    for filename in data.split(', '):
        download_checked.append(tk.BooleanVar())
        download_checked[-1].set(False)
        tk.Checkbutton(frame, text=filename, variable=download_checked[-1]).pack()
    tk.Label(frame, text='Download Section').pack()
    download_list.pack(side="top", fill="x")
    tk.Button(frame, text='Download').pack()

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