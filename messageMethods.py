import rsa
import socket

def sendRsa(message: str, publicKey: rsa.PublicKey, socket: socket.socket):
    encodedMessage = message.encode('utf-8')
    if len(encodedMessage) <= 53: # Message is short enough to send in one go
        encryptedMessage = rsa.encrypt(encodedMessage, publicKey)
        socket.sendall(encryptedMessage)
        return

    # Message is too long, split it into chunks
    fullEncryptedMessage = b""
    for i in range(0, len(encodedMessage), 53):
        chunk = encodedMessage[i:i+53]
        encryptedMessage = rsa.encrypt(chunk, publicKey)
        fullEncryptedMessage += encryptedMessage
    
    socket.sendall(fullEncryptedMessage)

def recieveRsa(privateKey: rsa.PrivateKey, socket: socket.socket):
    fullEncryptedMessage = socket.recv(1024)

    if not fullEncryptedMessage:
        print("Error: No message recieved")
        return None
    elif len(fullEncryptedMessage) <= 64:
        decryptedMessage = rsa.decrypt(fullEncryptedMessage, privateKey)
        return decryptedMessage.decode('utf-8')
    
    # Message is too long, split it into chunks
    FullDecryptedMessage = b""
    for i in range(0, len(fullEncryptedMessage), 64):
        chunk = fullEncryptedMessage[i:i+64]
        decryptedMessage = rsa.decrypt(chunk, privateKey)
        FullDecryptedMessage += decryptedMessage

    return FullDecryptedMessage.decode('utf-8')