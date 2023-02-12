import socket
import sys
import select
import thread

class ChatClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

    # method to register a new account, let user give parameters on command line?
    def register_account(self, username, password):
        # code here
        print("need to implement")
    
    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_message(self, recipient, message):
        msg_len = len(message)
        # need to figure out protocol stuff: max message length, how to 
        # indicate recipient, etc.


