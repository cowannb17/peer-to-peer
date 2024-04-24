import ast
import tkinter as tk
from tkinter import ttk
from client_connections import client as Client
from peer import peer as Peer

# creates client class which handles connections between server and client
client = Client()

peer = None

window = tk.Tk()
window.geometry("400x150")

frame = tk.Frame(window)

downloads = []


# Clears Tk window, needs to be run every time the window is changed
def clearFrame():
    for widget in frame.winfo_children():
        widget.destroy()


def find_combo_boxes(parent):
    combo_boxes = []
    stack = [parent]

    while stack:
        current = stack.pop()
        for widget in current.winfo_children():
            if isinstance(widget, ttk.Combobox):
                combo_boxes.append(widget)
            elif widget.winfo_children():
                stack.append(widget)
    
    return combo_boxes

def start_downloads(file_list):
    selection = [combo.get() for combo in find_combo_boxes(window)]
    files = [file[0] for file in file_list]
    clearFrame()
    
    global peer
    peer = Peer(client.user, False, files, selection)

def select_location_frame(file_list):
    # Changes window title
    window.title('Peer Client: Select Locations')

    # Creates a text label above the downloads section
    tk.Label(frame, text='Select where to download from').pack()

    location_selector_frame = tk.Frame(frame)
    i = 0
    for file in file_list:
        tk.Label(location_selector_frame, text=file[0]).grid(column=0, row=i)
        # Sets up dropdown box which selects the IP of the hosts
        combo = ttk.Combobox(location_selector_frame, state="readonly")
        # Gets IP from list of hosts
        combo['values'] = file[1]
        # Sets selection to first person
        combo.current(0)
        combo.grid(column=1, row=i)
        i += 1
    
    location_selector_frame.grid_columnconfigure(0, weight=1)
    location_selector_frame.grid_columnconfigure(1, weight=1)
    location_selector_frame.pack(side="top", fill="x")
    
    tk.Button(frame, text='Download', command=lambda: start_downloads(file_list), ).pack()
    tk.Button(frame, text='Go Back', command=lambda:[clearFrame(), offered_files_frame()]).pack()
    


# Method to request all checked downloads from the server, grabs the list of downloads and sends the list of checked to the server
def request_downloads():
    # Gets list of downloads, sorts by whether they are checked or not
    # i.e. groups checked and unchecked downloads together
    sort_by_checked = sorted(downloads, key=lambda file: file["checked"].get(), reverse=True)

    # Adds checked downloads to list until it runs into the first unchecked download
    # at which point all checked downloads have been added to the list
    checked_downloads = ""
    for file in sort_by_checked:
        if file["checked"].get() == False:
            break
        checked_downloads += file["filename"] + ","

    # Checks to see if no downloads are checked at all
    if (len(checked_downloads) == 0):
        return
    
    # Remove trailing commna
    checked_downloads = checked_downloads[:-1]

    # Gets list of users who have the target downloads
    download_users = client.get_download_users(checked_downloads)

    file_tuple_list = []
    i = 0

    for user_list in download_users.split("],"):
        if user_list[-1:] != "]":
            user_list += "]"
        
        # Convert list from string literal to actual list
        user_list = ast.literal_eval(user_list)

        # Insert tuple of file name and list of users who offer it into a list
        file_tuple_list.append((checked_downloads.split(",")[i], user_list))
        i += 1
    
    clearFrame()
    select_location_frame(file_tuple_list)
    


# Refreshes downloads list
def refresh_downloads():
    clearFrame()
    # resets downloads list
    global downloads
    downloads = []
    new_list = client.fetch_downloads_list()
    if new_list is not None:
        downloads = new_list
    offered_files_frame()


# Static frame setup of the file download frame, called every time the "See Downloadable Files" button is clicked
def offered_files_frame():
    # Changes window title
    window.title('Peer Client: Offered Files')

    # Creates a text label above the downloads section
    tk.Label(frame, text='Download Section').pack()
    
    # Creates the downloads list section as a new frame, 
    download_list = tk.Frame(frame)
    i = 0
    for download in downloads:
        tk.Checkbutton(download_list, text=download["filename"], variable=download["checked"]).grid(row=(i//3), column=(i % 3))
        i += 1
    
    if len(downloads) == 0:
        tk.Label(download_list, text="No Downloads were able to be found\nPerhaps there was a connection error.\nTry Again?").pack()
    
    # Packs the downloads list grid, uses three columns maximum
    for x in range(0, len(downloads)):
        if x >= 3:
            break
        download_list.grid_columnconfigure(x, weight=1)
    # Add download list to the frame
    download_list.pack(side="top", fill="x")
    
    # Add download and refresh buttons to the frame, refresh button
    tk.Button(frame, text='Find Peers', command=request_downloads).pack()
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

# Renders the window
w = root_window(client.first_connection())
temp_list = client.fetch_downloads_list()
if temp_list is not None:
    downloads = temp_list
frame.pack(side="top", expand=True, fill="both")
w.mainloop()