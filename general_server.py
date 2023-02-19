import socket
import random
import re

# import thread module
from _thread import *
import threading

MAX_MSG_LEN = 280
p_lock = threading.Lock()

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_sockets = {}
        self.accountName_table = {}
        self.uuid_dict = {}
        self.currentlyOnlineList = []

    def send_message(self, sock, message_type, status, message):
        print("sending")
        message_len = len(message)
        if message_len > MAX_MSG_LEN:
            print("Message too long")
        
        print("message len: " + str(chr(message_len)))
        print("status: " + str(chr(status)))
        
        to_send = chr(status) + chr(message_len)
        to_send += message_type + message
        print(to_send)
        assert(len(to_send) == 3 + len(message))
        sock.sendall(to_send.encode('UTF-8'))
    
    def send_response(self, sock, status, *args):
        self.send_message(sock, status, ":".join(args))

    def send_or_queue_message(self, message, user_from, user_to_send):
        cat_message = user_from + ":" + message
        if user_to_send not in self.accountName_table:
            return False
        user_to_send_sock = self.user_sockets[user_to_send]
        if user_to_send in self.currentlyOnlineList:
            self.send_message(user_to_send_sock, "C", 0, cat_message)
        #else: finish queueing messages later
        
        return True
    
    def create_account(self, username, pwd):  
        hashedPwd = hash(pwd) 
        if username in self.accountName_table:
            return False, -1
        else:
            # hashed for security
            pwdHash = hash(pwd)
            self.accountName_table[username] = pwdHash
            self.user_sockets[username] = None
            uuid = random.randint(0, 100)            
            return True, uuid
        
    def login(self, username, pwd, c):
        if username not in self.accountName_table:
            print("Invalid account name")
            return False
        elif hash(pwd) != self.accountName_table[username]:
            print("Invalid password")
            return False
        else:
            self.user_sockets[username] = c
            self.currentlyOnlineList.append(username)
            return True
    
    def get_by_wildcard(self, wildcard):
        regex = re.compile(wildcard)

    def threaded(self, c):
        while True:
            data = c.recv(1024)
            data_str = data.decode('UTF-8')
            if not data:
                print("No message received")
                break
            print(data_str + "\n")
            data_list = data_str.split("|")
            opcode = data_list[0]
            print("Opcode: " + str(opcode))

            if opcode == "1":
                accountName = str(data_list[1])
                accountPwd = str(data_list[2])
                
                success, uuid = self.create_account(accountName, accountPwd)
                if success:
                    self.uuid_dict[uuid] = accountName
                    self.send_message(c, "S", 0, chr(uuid))
                else:
                    self.send_message(c, "S", 1, "")
            elif opcode == "2":
                accountName = str(data_list[1])
                accountPwd = str(data_list[2])
                
                success = self.login(accountName, accountPwd, c)
                if success:
                    self.send_message(c, "S", 0, "")
                else:
                    self.send_message(c, "S", 1, "")

            elif opcode == "3":
                user_to_send = str(data_list[1])
                message = str(data_list[2])
                args = message.split(":")
                # change this
                from_uuid = int(args[0])
                user_from = self.uuid_dict[from_uuid]
                print(user_from)

                success = self.send_or_queue_message(args[1], user_from, user_to_send)
                if success:
                    self.send_message(c, "S", 0, "")
                else:
                    self.send_message(c, "S", 1, "")

            elif opcode == "4": 
                # fetch buffered messages, if any
                print("implement")
            elif opcode == "5":
                # search by text wildcard
                print("implement")
            else:
                # delete account
                print("implement")
            
        c.close()

    def start_server(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Socket is listening")

        while True:
            c, addr = self.socket.accept()
            print("connected to: ", addr[0], ": ", addr[1])

            start_new_thread(self.threaded, (c,))
        self.socket.close()


if __name__ == "__main__":
    HOST, PORT = "localhost", 2048
    chat_server = ChatServer(HOST, PORT)
    chat_server.start_server()