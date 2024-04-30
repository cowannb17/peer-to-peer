import rsa

class RSAKeyExchange:
    def __init__(self, key_size=512):
        self.public_key, self.private_key = rsa.newkeys(key_size)

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key
    
    
    