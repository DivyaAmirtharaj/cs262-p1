import socket
import mysql.connector
import random

# import thread module
from _thread import *
import threading

MAX_MSG_LEN = 280
p_lock = threading.Lock()

class ChatServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_sockets = {}
        self.accountName_table = {}
        self.uuid_dict = {}
        self.currentlyOnlineList = []

    def send_message(self, sock, message_type, status, message):
        message_len = len(message)
        if message_len > MAX_MSG_LEN:
            print("Message too long")
        
        to_send = message_type + chr(status) + chr(message_len) + message
        sock.sendall(to_send)
    
    def send_response(self, sock, status, *args):
        self.send_message(sock, status, ":".join(args))

    def send_or_queue_message(self, message, user_from, user_to_send):
        if user_to_send not in self.accountName_table:
            return False
        user_to_send_sock = user_sockets[user_to_send]
        if user_to_send in currentlyOnlineList:
            self.send_message(user_to_send_sock, "C", 0, message)
        
        return True
        #else: finish queueing messages later
    
    def create_account(self, username, pwd):  
        hashedPwd = hash(pwd) 
        if username in self.accountName_table:
            return False, -1
        else:
            # hashed for security
            pwdHash = hash(accountPwd)
            self.accountName_table[accountName] = pwdHash
            self.user_sockets[accountName] = None
            uuid = random.randint(0, 100)
            print("New account: " + accountName)
            
            return True, uuid
        
    def login(self, username, pwd):
        if accountName not in accountName_table:
            print("Invalid account name")
            return False
        elif hashedPwd != self.accountName_table[accountName]:
            print("Invalid password")
            return False
        else:
            self.user_sockets[accountName] = c
            self.currentlyOnlineList.append(accountName)
            return True

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
                if len(data_list) < 3:
                    self.send_message(c, 2, "Not enough params")
                else:
                    accountName = str(data_list[1])
                    accountPwd = str(data_list[2])
                    
                    success, uuid = self.create_account(accountName, accountPwd)
                    if success:
                        self.uuid_dict[uuid] = accountName
                        self.send_message(c, "S", 0, chr(uuid))
                    else:
                        self.send_message(c, "S", 1, "Failed account creation")
            elif opcode == "2":
                if len(data_list) < 3:
                    self.send_message(c, 2, "Not enough params")
                else: 
                    accountName = str(data_list[1])
                    accountPwd = str(data_list[2])
                    
                    success = self.login(accountName, accountPwd)
                    if success:
                        self.send_message(c, "S", 0, "")
                    else:
                        self.send_message(c, "S", 1, "Failed login")

            elif opcode == "3":
                if len(data_list) < 3:
                    self.send_message(c, "S", 2, "Not enough params")
                else:
                    user_to_send = str(data_list[1])
                    message = str(data_list[2])
                    args = message.split(":")
                    # change this
                    from_uuid = args[0]
                    user_from = self.uuid_dict[from_uuid]

                    success = self.send_or_queue_message(message, user_from, user_to_send)
                    if success:
                        self.send_message(c, "S", 0, "")
                    else:
                        self.send_message(c, "S", 1, "Recipient does not exist")

            elif opcode == "4": 
                # fetch buffered messages, if any
            elif opcode == "5":
                # search by text wildcard
            elif opcode == "6":
                # delete account
            else:
                data = "Invalid Opcode\n"
            
        c.close()


if __name__ == "__main__":