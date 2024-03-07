import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import sys
import os
import time
class EncryptedMessagingClient:
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.username = username
        self.register(username, password)
        self.private_key, self.public_key = self.generate_key_pair()
        self.register_public_key(self.public_key)

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key, pem.decode('utf-8')

    def register(self, username, password):
        response = requests.post(f"{self.server_url}/register", json={'username': username, 'password': password})
        print(response.json())

    def register_public_key(self, public_key_pem):
        response = requests.post(f"{self.server_url}/register_key", json={'username': self.username, 'public_key': public_key_pem})
        print(response.json())

    def fetch_public_key(self, username):
        response = requests.post(f"{self.server_url}/get_public_key", json={'username': username})
        if response.status_code == 200:
            public_key_pem = response.json()['public_key']
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            return public_key
        else:
            print("Could not fetch public key for:", username)
            return None

    def send_message(self, receiver, message):
        recipient_public_key = self.fetch_public_key(receiver)
        if recipient_public_key:
            encrypted_message = recipient_public_key.encrypt(
                message.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            response = requests.post(f"{self.server_url}/send", json={'sender': self.username, 'receiver': receiver, 'encrypted_message': encrypted_message.hex()})
            print(response.json())

    def receive_messages(self):
        response = requests.post(f"{self.server_url}/receive", json={'receiver': self.username})
        messages = response.json()['messages']
        for msg in messages:
            sender, _, encrypted_message_hex = msg
            encrypted_message = bytes.fromhex(encrypted_message_hex)
            decrypted_message = self.private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print(f"From {sender}: {decrypted_message.decode('utf-8')}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python newclient.py <server_url> <username> <password>")
        sys.exit(1)
    os.system('clear')    
    receiver = input("Enter the receiver's username: ")
    os.system('clear')
    server_url, username, password = sys.argv[1:]
    client = EncryptedMessagingClient(server_url, username, password)
    client.receive_messages()
    while True:
        

        message = input("Enter your message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client.send_message(receiver, message)
        #print("Messages received:")
        time.sleep(2)
        os.system('clear') #new
        print("Messages received:")
        client.receive_messages()
