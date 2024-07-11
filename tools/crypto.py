from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

GenKey = lambda: base64.urlsafe_b64encode(get_random_bytes(32))

def Encrypt(data, key):
	cipher = AES.new(base64.urlsafe_b64decode(key), AES.MODE_EAX)
	nonce = cipher.nonce
	ciphertext, tag = cipher.encrypt_and_digest(data)
	return base64.urlsafe_b64encode(nonce + tag + ciphertext)

def Decrypt(data, key):
	token = base64.urlsafe_b64decode(data)
	nonce, tag, ciphertext = token[:16], token[16:32], token[32:]
	cipher = AES.new(base64.urlsafe_b64decode(key), AES.MODE_EAX, nonce=nonce)
	return cipher.decrypt_and_verify(ciphertext, tag)
