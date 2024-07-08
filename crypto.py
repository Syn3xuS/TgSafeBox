from cryptography.fernet import Fernet

GenKey = lambda: Fernet.generate_key()
Encrypt = lambda data, key: Fernet(key).encrypt(data)
Decrypt = lambda token, key: Fernet(key).decrypt(token)