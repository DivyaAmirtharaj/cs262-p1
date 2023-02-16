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
        self.currentlyOnlineList = []

    def send_message(self, sock, message):
        message_len = len(message)
        if message_len > MAX_MSG_LEN:
            print("Message too long")
        
        to_send = chr(message_len) + message
        sock.sendall(to_send)

    def send_or_queue_message(self, message, user_from, user_to_send):
        user_to_send_sock = user_sockets[user_to_send]
        if user_to_send in currentlyOnlineList:
            data = self.send_message(user_to_send_sock, message)
        #else: finish queueing messages later


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
                    data = "Did not provide a valid account name or password"
                else:
                    accountName = str(data_list[1])
                    accountPwd = str(data_list[2])
                    
                    if accountName in accountName_table:
                        data = "Account name already taken\n"
                    else:
                        # hashed for security
                        pwdHash = hash(accountPwd)
                        self.accountName_table[accountName] = pwdHash
                        self.currentlyOnlineList.append(accountName)
                        sockets_by_user[accountName] = None
                        print("New account: " + accountName)
                        data = "Account " + accountName + "created\n"
            elif opcode == "2":
                if len(data_list) < 3:
                    data = "Did not provide a valid account name or password\n"
                else: 
                    accountName = str(data_list[1])
                    accountPwd = str(data_list[2])
                    hashedPwd = hash(accountPwd)
                    
                    if accountName not in accountName_table:
                        print("Invalid account name")
                        data = "Account name " + accountName + " not registered\n"
                    elif hashedPwd != self.accountName_table[accountName]:
                        print("Invalid password")
                        data = "Account name " + accountName + " password was incorrect\n"
                    else:
                        self.user_sockets[accountName] = c
                        self.currentlyOnlineList.append(accountName)
                        data = "Logged in successfully!"
            elif opcode == "3":
                if len(data_list) < 3:
                    data = "Did not provide a valid recipient or message\n"
                else:
                    sendAccount = str(data_list[1])
                    message = str(data_list[2])
                    self.send_message()

            elif opcode == "4": 
                # fetch buffered messages, if any
            elif opcode == "5":
                # search by text wildcard
            elif opcode == "6":
                # delete account
            else:
                data = "Invalid Opcode\n"
            
            c.send(data.encode('ascii'))
        c.close()