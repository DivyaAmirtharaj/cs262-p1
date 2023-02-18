import socket
import sys
import select
import thread
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
        
        message_type, status, message_len = header[0], header[1], header[2]

        received_message = self.get_k_bytes(sock, ord(message_len))
        status = ord(status)

        return message_type, status, received_message
    
    def get_k_bytes(self, sock, k):
        total_bytes = 0
        received_message = ""

        while total_bytes < k:
            data = sock.recv(1, socket.MSG_PEEK)

            if len(data) == 0:
                # change this to a real error
                print("Client died")
                break
            else:
                next_recv = sock.recv(n - total_bytes)
                total_bytes += len(next_recv)
                received_message += next_recv
        
        assert(total_bytes == k)

        return received_message


    def listener(self):
        while True: 
            message_type, status, received_message = self.recv_from_server(self.socket)
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
        thread.start_new_thread(self.listener, ())
    
    def send_and_get_response(self, data):
        self.sock.send(data.encode('ascii'))
        status, response = self.get_server_response()
        return status, response

    def get_server_response(self):
        try:
            status, response = self.response_queue.get(block=True, timeout=3)
            return status, response
        except queue.Empty:
            return 3, None

    
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
                    if len(data_list) < 3:
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
                    if len(data_list) < 3:
                        print("Incorrect parameters: correct form is 2|[username]|[pwd]")
                    else:
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            self.login = True
                            print("Logged into account " + self.username)
                        else:
                            print("Incorrect username or password.")
                # sending message
                elif opcode == "3":
                    if len(data_list) < 3:
                        print("Incorrect parameters: correct form is 3|[user_to_send]|[message]")
                    else:
                        # add the uuid of this user so that it can be decoded by
                        # the server and sent
                        to_user = args[0]
                        ans = "|".join([opcode, to_user, str(self.uuid) + ":" + args[1]])
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            print("Delivered message to " + to_user)
                        else:
                            print("Could not deliver to " + to_user + ". Check if this username exists")
                elif opcode == "4":
                    # fetch buffered messages
                elif opcode == "5":
                    # search by text wildcard
                elif opcode == "6":
                    # delete account
                else:
                    print("Invalid opcode. 1 = create account, 2 = login, 3 = send, 4 = fetch, 5 = search, 6 = delete")
                continue
        # close the connection
        s.close()

if __name__ == "__main__":
    


