import rsa
import socket

def sendRsa(message, publicKey: rsa.PublicKey, socket: socket.socket):
    if type(message) != bytes:
        encodedMessage = message.encode('utf-8')
    else:
        encodedMessage = message

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

def decrypt_message(fullEncryptedMessage: str, privateKey: rsa.PrivateKey):
    if len(fullEncryptedMessage) <= 64:
        decryptedMessage = rsa.decrypt(fullEncryptedMessage, privateKey)
        return decryptedMessage
    
    # Message is too long, split it into chunks
    fullDecryptedMessage = b""
    for i in range(0, len(fullEncryptedMessage), 64):
        chunk = fullEncryptedMessage[i:i+64]
        decryptedMessage = rsa.decrypt(chunk, privateKey)
        fullDecryptedMessage += decryptedMessage

    return fullDecryptedMessage

def recieveRsa(privateKey: rsa.PrivateKey, socket: socket.socket):
    fullEncryptedMessage = socket.recv(1024)

    if not fullEncryptedMessage:
        print("Error: No message recieved")
        return None

    FullDecryptedMessage = decrypt_message(fullEncryptedMessage, privateKey)

    return FullDecryptedMessage.decode('utf-8')

def recieveFileRsa(privateKey: rsa.PrivateKey, socket: socket.socket):
    fullEncryptedMessage = b''
    while True:
        encryptedMessage = socket.recv(1024)
        
        yield len(encryptedMessage)
        fullEncryptedMessage += encryptedMessage

        if not encryptedMessage:
            yield "end"
            fullDecryptedMessage = decrypt_message(fullEncryptedMessage, privateKey)
            yield fullDecryptedMessage
            break

        



