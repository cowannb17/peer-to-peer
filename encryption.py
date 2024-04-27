from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class encryption:
    def __init__(self):
        self.key = get_random_bytes(32) # 256 bit key
        self.cipher = AES.new(self.key, AES.MODE_EAX)
        self.nonce = self.cipher.nonce

    def encrypt(self, message):
        ciphertext, tag = self.cipher.encrypt_and_digest(message)
        return ciphertext, tag

    def decrypt(self, ciphertext, tag):
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=self.nonce)
        plaintext = cipher.decrypt(ciphertext)
        try:
            cipher.verify(tag)
            return plaintext
        except ValueError:
            return False

    def get_key(self):
        return self.key

    def get_nonce(self):
        return self.nonce