import socket
import random
import re
from database import Database

# import thread module
from _thread import *
import threading

MAX_MSG_LEN = 280
p_lock = threading.Lock()
LOGGED_IN = 1
LOGGED_OUT = 0

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_sockets = {}
        self.accountName_table = {}
        self.uuid_dict = {}
        self.currentlyOnlineList = []
        self.db = Database()
        self.db.delete_table()
        self.db.create_table()
    
    def check_user_in_db(self, username):
        try: 
            uuid_exists = self.db.get_uuid(username)
        except Exception as e:
            print("Username is invalid")
            print(e)
            return False
        return True

    def send_message(self, sock, message_type, status, message):
        message_len = len(message)
        if message_len > MAX_MSG_LEN:
            print("Message too long")
            return False
        
        to_send = chr(status) + chr(message_len)
        to_send += message_type + message
        print(to_send)
        assert(len(to_send) == 3 + len(message))
        sock.sendall(to_send.encode('UTF-8'))
        return True
    
    def send_response(self, sock, status, *args):
        self.send_message(sock, status, ":".join(args))

    def send_or_queue_message(self, message, user_from, user_to_send):
        cat_message = user_from + ":" + message
        if self.check_user_in_db(user_to_send):
            user_to_send_sock = self.user_sockets[user_to_send]
        else:
            return False, 1

        if self.db.is_logged_in(user_to_send):
            result = self.send_message(user_to_send_sock, "C", 0, cat_message)
            if not result:
                return False, 2
        else:
            self.db.add_message(user_from, user_to_send, cat_message)
        
        return True, 0
    
    def create_account(self, username, pwd):  
        pwdHash = hash(pwd)
        print(pwdHash)
        self.user_sockets[username] = None
        try:
            self.db.add_users(username, pwdHash, LOGGED_OUT)
        except Exception as e:
            print(e)
            print("repeat user")
            return False, -1
        uuid = self.db.get_uuid(username)
        return True, uuid
        
    def login(self, username, pwd, c):
        user_exists = self.check_user_in_db(username)
        if not user_exists:
            return False, 1
        elif self.db.is_logged_in(username):
            return False, 2
        pwdHash = hash(pwd)
        print(pwdHash)
        try:
            self.user_sockets[username] = c
            self.db.update_login(username, pwdHash, LOGGED_IN)
            uuid = self.db.get_uuid(username)
            return True, uuid
        except Exception as e:
            print(e)
            return False, 3
    
    def recv_from_socket(self, c):
        data = c.recv(1, socket.MSG_PEEK)

        if len(data) == 0:
            raise Exception("Client died")
        data = c.recv(1024)
        return data
    
    def get_by_wildcard(self, wildcard):
        regex = re.compile(wildcard)

    def threaded(self, c):
        while True:
            try:
                data = self.recv_from_socket(c)
            except Exception as e:
                print(e)
                print("Client died")
                lost_user = list(self.user_sockets.keys())[list(self.user_sockets.values()).index(c)]
                self.db.force_logout(lost_user)
                self.user_sockets[lost_user] = None
                break

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
                    self.send_message(c, "S", 0, chr(uuid))
                else:
                    self.send_message(c, "S", 1, "")
            elif opcode == "2":
                accountName = str(data_list[1])
                accountPwd = str(data_list[2])
                
                success, uuid_or_status = self.login(accountName, accountPwd, c)
                if success:
                    self.send_message(c, "S", 0, chr(uuid_or_status))
                else:
                    self.send_message(c, "S", uuid_or_status, "")

            elif opcode == "3":
                user_to_send = str(data_list[1])
                message = str(data_list[2])
                args = message.split(":")
                from_uuid = int(args[0])
                text_message = args[1]
                print(from_uuid)

                try:
                    user_from = self.db.get_username(from_uuid)
                except Exception as e:
                    print("User has been deleted")
                    self.send_message(c, "S", 2, "")
                    continue

                success = self.send_or_queue_message(text_message, user_from, user_to_send)
                if success:
                    self.send_message(c, "S", 0, "")
                else:
                    self.send_message(c, "S", 1, "")

            elif opcode == "4":
                username = str(data_list[1])
                all_history = self.db.get_all_history(username)
                all_history_message = '\n'.join([str(msg) for msg in all_history])
                success = self.send_or_queue_message(all_history_message, "", username)
                if success:
                    self.send_message(c, "S", 0, "")
                else:
                    self.send_message(c, "S", 1, "")
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