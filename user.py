class user:
    def __init__(self, userID, userIP): # currently these parameters are not used
        self.userID = None
        self.userIP = None
        self.requestedFiles = []
        self.downloads = []

    def requestFiles(self, files):
        self.requestedFiles = [] # A list of files that the user wants to download

    def fileDownload(self, file):
        self.downloads.append(file)


