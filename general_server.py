import socket
import mysql.connector
import random

# import thread module
from _thread import *
import threading

accountName_table = {}
currentlyOnlineList = []

p_lock = threading.Lock()

def threaded(c):
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
            elif len(data_list) > 3:
                data = "Too many parameters. Account name and password cannot contain a | character.\n"
            else:
                accountName = str(data_list[1])
                accountPwd = str(data_list[2])
                
                if accountName in accountName_table:
                    data = "Account name already taken\n"
                else:
                    # hashed for security
                    pwdHash = hash(accountPwd)
                    accountName_table[accountName] = pwdHash
                    currentlyOnlineList.append(accountName)
                    print("New account: " + accountName)
                    data = "Account " + accountName "created and logged in\n"
        elif opcode == "2":
            if len(data_list) < 3:
                data = "Did not provide a valid account name or password\n"
            elif len(data_list) > 3:
                data = "Too many parameters. Account name and password cannot contain a | character.\n"
            else: 
                accountName = str(data_list[1])
                accountPwd = str(data_list[2])
                hashedPwd = hash(accountPwd)
                
                if accountName not in accountName_table:
                    print("Invalid account name")
                    data = "Account name " + accountName + " not registered\n"
                elif hashedPwd != accountName_table[accountName]:
                    print("Invalid password")
                    data = "Account name " + accountName + " password was incorrect\n"
                else:
                    currentlyOnlineList.append(accountName)
        elif opcode == "3":
            # send or queue messages
        elif opcode == "4": 
            # fetch buffered messages, if any
        elif opcode == "5":
            # search by text wildcard
        elif opcode == "6":
            # delete account
        else:
            data = "Invalid Opcode\n"