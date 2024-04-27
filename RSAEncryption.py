import rsa

# Generate a new key pair
(public_key, private_key) = rsa.newkeys(512)

# Encrypt a message
message = 'Hello, world!'
encrypted_message = rsa.encrypt(message.encode(), public_key)

# Decrypt the message
decrypted_message = rsa.decrypt(encrypted_message, private_key)

print(decrypted_message.decode())  # prints 'Hello, world!'