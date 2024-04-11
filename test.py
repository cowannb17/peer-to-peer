# this is a test file

#we are on test branch

import keyring

def save_user_id(user_id):
    keyring.set_password("p2p", "uuid", user_id)

def load_user_id():
    user_id = keyring.get_password("p2p", "uuid")
    return user_id

# Check if the keyring has been created
user_id = load_user_id()
if user_id is None:
    print("No user ID found. This might be the first run of the program.")
else:
    print("User ID:", user_id)