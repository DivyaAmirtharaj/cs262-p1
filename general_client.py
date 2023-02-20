import socket
import sys
import select
from _thread import *
import threading
import random
import queue

NUM_BYTES_IN_HEADER = 3

class ChatClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.uuid = None
        self.login = False
        # helps to keep track of info that the server sends the
        # client that is necessary to set up the client, like
        # uuid and login status
        self.server_responses = queue.Queue()

    def recv_from_server(self, sock):
        header = self.get_k_bytes(sock, NUM_BYTES_IN_HEADER)

        
        status, message_len, message_type = header[0], header[1], header[2]

        received_message = self.get_k_bytes(sock, ord(message_len))
        status = ord(status)

        return message_type, status, received_message
    
    def get_k_bytes(self, sock, k):
        total_bytes = 0
        received_message = ""

        while total_bytes < k:
            data = sock.recv(1, socket.MSG_PEEK).decode('UTF-8')
            if len(data) == 0:
                raise Exception("client died")
                break
            else:
                next_recv = sock.recv(k - total_bytes).decode('UTF-8')
                total_bytes += len(next_recv)
                received_message += next_recv
        
        assert(total_bytes == k)

        return received_message


    def listener(self):
        while True: 
            try:
                message_type, status, received_message = self.recv_from_server(self.socket)
            except Exception as e:
                print("You've been disconnected")
                exit()
            # insert an exception for client death
            if message_type == "C":
                sys.stdout.write(received_message + "\n")
            elif message_type == "S":
                self.server_responses.put((status, received_message))
            else:
                # make this an exception
                print("bad message format")
    
    def connect(self):
        self.socket.connect((self.host, self.port))
        start_new_thread(self.listener, ())
    
    def send_and_get_response(self, data):
        self.socket.send(data.encode('ascii'))
        status, response = self.get_server_response()
        return status, response

    def get_server_response(self):
        try:
            status, response = self.server_responses.get(block=True, timeout=3)
            return status, response
        except queue.Empty:
            print("empty")
            return 4, None
    
    def run_client(self):
        while True:
            ans = input('\n> ')
            if ans == '':
                ans2 = input('\nDo you want to continue(y/n) :')
                if ans2 =='y':
                    continue
                else:
                    break
            else:
                args = ans.split("|")
                opcode = args[0]

                # creating an account
                if opcode == "1":
                    if len(args) < 3:
                        print("Incorrect parameters: correct form is 1|[username]|[pwd]")
                    else:
                        username = args[1]
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            self.uuid = ord(response)
                            self.username = username
                            print("Created account " + username)
                        else:
                            print("Username already exists. Pick a different one.")
                # logging in
                elif opcode == "2":
                    if len(args) < 3:
                        print("Incorrect parameters: correct form is 2|[username]|[pwd]")
                    else:
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            if not self.username:
                                self.username = args[1]
                            if not self.uuid:
                                self.uuid = ord(response)
                            self.login = True
                            print("Logged into account")
                        elif status == 1:
                            print("Incorrect username.")
                        elif status == 2:
                            print("Already logged in.")
                        elif status == 3:
                            print("Incorrect password.")
                        else:
                            print("Unable to login")
                # sending message
                elif opcode == "3":
                    if len(args) < 3:
                        print("Incorrect parameters: correct form is 3|[user_to_send]|[message]")
                    elif not self.login:
                        print("Must be logged in to perform this action")
                    else:
                        # add the uuid of this user so that it can be decoded by
                        # the server and sent
                        to_user = args[1]
                        ans = "|".join([opcode, to_user, str(self.uuid) + ":" + args[2]])
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            print("Delivered message to " + to_user)
                        elif status == 1:
                            print("Could not deliver to " + to_user + ". Check if this username exists")
                        elif status == 2:
                            print("Message was too long. Keep messages under 280 characters.")
                        else:
                            print("Unable to send message")
                elif opcode == "4":
                    if not self.login:
                        print("Must be logged in to perform this action")
                    else:
                        status, response = self.send_and_get_response(ans + "|" + self.username)
                        if status == 0:
                            print("Retrieved all history for " + self.username)
                        elif status == 1:
                            print("No unread messages")
                        else:
                            print("Unable to retrieve history")
                elif opcode == "5":
                    if len(args) < 2:
                        print("Incorrect parameters: correct form is 5|[regex_wildcard]")
                    else:
                        status, response = self.send_and_get_response(ans + "|" + self.username)
                        if status == 0:
                            print("Found all matching users")
                        elif status == 1:
                            print("No matching users")
                        else:
                            print("Unable to retrieve matching users")
                elif opcode == "6":
                    print("implement")
                    # delete account
                else:
                    print("Invalid opcode. 1 = create account, 2 = login, 3 = send, 4 = fetch, 5 = search, 6 = delete")
                continue
        # close the connection
        s.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 2048
    chat_client = ChatClient(HOST, PORT)
    chat_client.connect()
    chat_client.run_client()
    


