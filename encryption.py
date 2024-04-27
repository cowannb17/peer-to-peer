from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class encryption:
    def __init__(self):
        """
        Initializes an encryption object with a randomly generated key and nonce.
        
        """
        self.key = get_random_bytes(32) # 256 bit key
        self.cipher = AES.new(self.key, AES.MODE_EAX)
        self.nonce = self.cipher.nonce

    def encrypt(self, message):
        """
        Encrypts the given message using the AES encryption algorithm.

        Args:
            message (bytes): The plaintext message to be encrypted.

        Returns:
            tuple: A tuple containing the ciphertext and the authentication tag.

        Raises:
            None

        """
        ciphertext, tag = self.cipher.encrypt_and_digest(message)
        return ciphertext, tag

    def decrypt(self, ciphertext, tag):
        """
        Decrypts the given ciphertext using the AES encryption algorithm.

        Args:
            ciphertext (bytes): The encrypted ciphertext to be decrypted.
            tag (bytes): The authentication tag associated with the ciphertext.

        Returns:
            bytes or bool: The decrypted plaintext if the decryption is successful, False otherwise.

        Raises:
            None

        """
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=self.nonce)
        plaintext = cipher.decrypt(ciphertext)
        try:
            cipher.verify(tag)
            return plaintext
        except ValueError:
            return False  # The encryption key is incorrect, the message was tampered with, or the message was corrupted
    
    def get_key(self):
        return self.key

    def get_nonce(self):
        return self.nonce

    def export_key(self, recipient_public_key):
        """
        Encrypts the AES key with the recipient's public RSA key.

        Args:
            recipient_public_key (str): The recipient's public RSA key.

        Returns:
            bytes: The encrypted AES key.

        """
        rsa_public_key = RSA.import_key(recipient_public_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
        encrypted_key = cipher_rsa.encrypt(self.key)
        return encrypted_key

    def import_key(self, encrypted_key, recipient_private_key):
        """
        Imports and decrypts an AES key using the recipient's private RSA key.

        Args:
            encrypted_key (bytes): The encrypted AES key.
            recipient_private_key (str): The recipient's private RSA key.

        Returns:
            None

        Raises:
            ValueError: If the recipient's private key is invalid or the decryption fails.
        """
        rsa_private_key = RSA.import_key(recipient_private_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
        self.key = cipher_rsa.decrypt(encrypted_key)