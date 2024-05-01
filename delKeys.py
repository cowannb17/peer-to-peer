import keyring

# print keyring

print("pubkey: ", keyring.get_password("p2p", "pubkey"))
print("privkey: ", keyring.get_password("p2p", "privkey"))
print("server_pubkey: ", keyring.get_password("p2p", "server_pubkey"))
print("uuid: ", keyring.get_password("p2p", "uuid"))


def delete_password(service, username):
    if keyring.get_password(service, username) is not None:
        keyring.delete_password(service, username)

delete_password("p2p", "pubkey")
delete_password("p2p", "privkey")
delete_password("p2p", "server_pubkey")
delete_password("p2p", "uuid")

print("pubkey: ", keyring.get_password("p2p", "pubkey"))
print("privkey: ", keyring.get_password("p2p", "privkey"))
print("server_pubkey: ", keyring.get_password("p2p", "server_pubkey"))
print("uuid: ", keyring.get_password("p2p", "uuid"))