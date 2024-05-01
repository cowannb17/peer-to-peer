import keyring

# print keyring
pubkey = keyring.get_password("p2p", "pubkey")
privkey = keyring.get_password("p2p", "privkey")
server_pubkey = keyring.get_password("p2p", "server_pubkey")
uuid = keyring.get_password("p2p", "uuid")

print("pubkey: ", pubkey)
print("privkey: ", privkey)
print("server_pubkey: ", server_pubkey)
print("uuid: ", uuid)

def delete_password(service, username):
    if keyring.get_password(service, username) is not None:
        keyring.delete_password(service, username)

delete_password("p2p", "pubkey")
delete_password("p2p", "privkey")
delete_password("p2p", "server_pubkey")
delete_password("p2p", "uuid")

print("pubkey: ", pubkey)
print("privkey: ", privkey)
print("server_pubkey: ", server_pubkey)
print("uuid: ", uuid)