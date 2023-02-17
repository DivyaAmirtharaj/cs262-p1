import socket
import sys
import select
import thread
import random

class ChatClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.uuid = None
        self.online = False

    # method to register a new account, let user give parameters on command line?
    def register_account(self, username, password):
        # code here
        print("need to implement")
    
    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_message(self, recipient, message):
        msg_len = len(message)
        


