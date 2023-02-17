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

    def recv_from_server(self, socket):
        # finish

    def listener(self):
        """
        Listens forever for new messages from users delivered through the server
        and server responses. New messages are directly printed to stdout, server
        responses are queue'd up to be handled later
        """
        while True: 
            status, message = self.recv_from_server(self.socket)

    
    # method to register a new account, let user give parameters on command line?
    def create_account(self, username, password):
        
    
    def connect(self):
        self.socket.connect((self.host, self.port))
        thread.start_new_thread(self.listener, ())

    def send_message(self, recipient, message):
        msg_len = len(message)
        


