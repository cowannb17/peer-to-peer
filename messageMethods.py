import rsa
import socket

def sendRsa(message: str, publicKey: rsa.PublicKey, socket: socket.socket):
    encodedMessage = message.encode('utf-8')
    encryptedMessage = rsa.encrypt(encodedMessage, publicKey)
    socket.sendall(encryptedMessage)

def recieveRsa(privateKey: rsa.PrivateKey, socket: socket.socket):
    encryptedMessage = socket.recv(1024)
    decryptedMessage = rsa.decrypt(encryptedMessage, privateKey)
    return decryptedMessage.decode('utf-8')