import rsa
import socket

def sendRsa(message: str, publicKey: rsa.PublicKey, socket: socket.socket):
    encodedMessage = message.encode('utf-8')
    if len(encodedMessage) <= 53: # Message is short enough to send in one go
        encryptedMessage = rsa.encrypt(encodedMessage, publicKey)
        socket.sendall(encryptedMessage)
        return

    # Message is too long, split it into chunks
    for i in range(0, len(encodedMessage), 53):
        chunk = encodedMessage[i:i+53]
        encryptedMessage = rsa.encrypt(chunk, publicKey)
        socket.sendall(encryptedMessage)
    
    sendRsa("file_end", publicKey, socket) # Send a message to indicate the end of the file


def recieveRsa(privateKey: rsa.PrivateKey, socket: socket.socket):
    encryptedMessage = socket.recv(1024)
    decryptedMessage = rsa.decrypt(encryptedMessage, privateKey)
    return decryptedMessage.decode('utf-8')