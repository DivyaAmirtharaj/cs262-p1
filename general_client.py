import socket
import sys
import select
from _thread import *
import threading
import random
import queue

NUM_BYTES_IN_HEADER = 3

class ChatClient:
    """
    Implements a chat client/user that connects to the server using a socket. 
    Clients possess an associated username and UUID (which is retrieved through
    creating an account with the server). Clients submit requests to the server
    and message other clients through the command line.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.uuid = None
        self.login = False
        # helps to keep track of info that the server sends the
        # client that is necessary to set up the client, like
        # uuid and login status (which may be sent through server responses)
        # also contains general server confirmation responses
        self.server_responses = queue.Queue()

    def recv_from_server(self, sock):
        """
        Receives a message formatted according to our wire protocol: a message
        should contain a 3-byte header:
            1st byte: status code (from server)
            2nd byte: message length encoded as a unicode char
            3rd byte: single char 'C' or 'S' that indicates if 
            the received message is a message from another user or a server response
        Reads the header and then the message by reading in fixed numbers of bytes
        from the server

        return: string message type, int status, string message received
        """

        # receive the header first
        header = self.get_k_bytes(sock, NUM_BYTES_IN_HEADER)
        status, message_len, message_type = header[0], header[1], header[2]

        # convert message length back to integer
        received_message = self.get_k_bytes(sock, ord(message_len))
        status = ord(status)

        return message_type, status, received_message
    
    def get_k_bytes(self, sock, k):
        """
        Receives k bytes from the server. Used to receive the (fixed-length) header
        and (known-length) messages from the server. Blocks until finished reading

        return: string received message
        """
        total_bytes = 0
        received_message = ""

        while total_bytes < k:
            # Try to read one byte in order to see if the client has died
            # Peek prevents this singular byte from actually being retrieved
            data = sock.recv(1, socket.MSG_PEEK).decode('UTF-8')
            if len(data) == 0:
                raise Exception("client died")
                break
            else:
                # if everything is fine, continue reading until the 
                # total number of requested bytes has been read
                next_recv = sock.recv(k - total_bytes).decode('UTF-8')
                total_bytes += len(next_recv)
                received_message += next_recv
        
        assert(total_bytes == k)

        return received_message

    def listener(self):
        """
        Called once the client is started in a separate thread so it can listen
        for input from the server. Constantly receives from the server
        """
        while True: 
            try:
                message_type, status, received_message = self.recv_from_server(self.socket)
            except Exception as e:
                # if nothing is received from the server, then the client has died
                # we assume that the server never dies
                exit()
            # insert an exception for client death
            if message_type == "C":
                sys.stdout.write(received_message + "\n")
            elif message_type == "S":
                self.server_responses.put((status, received_message))
            else:
                print("Bad message format")
    
    def connect(self):
        """
        Connects to the server host and port and starts listening
        """
        self.socket.connect((self.host, self.port))
        start_new_thread(self.listener, ())
    
    def send_and_get_response(self, data):
        """
        Sends ascii-encoded data from the client and then pops the most recent
        queued message from the server immediately after (this works because
        sockets preserve order)

        return: Int status of operation from server, server's textual response
        """
        self.socket.send(data.encode('ascii'))
        status, response = self.get_server_response()
        return status, response

    def get_server_response(self):
        """
        Tries to retrieve a server's response from the server responses queue.
        
        return: Int status of operation from server, server's textual response
        """
        try:
            status, response = self.server_responses.get(block=True, timeout=10)
            return status, response
        except queue.Empty:
            # if the queue has nothing in it, then an error has occurred
            print("Queue empty")
            return 4, None
    
    def run_client(self):
        """
        Called by main client thread to constantly prompt input from the client, do some
        basic verification (e.g. correct arguments), and send client requests/input
        to the server. Supports 6 operations: create account, login, send message
        to another user, retrieve message history, search usernames by text wildcard,
        and delete account. 

        Valid requests are formatted as follows: [operation code]|[arg1]|[arg2]...
        """
        while True:
            # ask for input
            ans = input('\n> ')
            if ans == '':
                ans2 = input('\nDo you want to continue(y/n) :')
                if ans2 =='y':
                    continue
                else:
                    break
            else:
                # retrieve arguments and operation code
                args = ans.split("|")
                opcode = args[0]

                # creating an account
                if opcode == "1":
                    if len(args) < 3:
                        print("Incorrect parameters: correct form is 1|[username]|[pwd]")
                    elif self.login or self.username is not None:
                        # do not allow account creation while logged in or associated
                        # with another account -- 1 account per client
                        print("Already logged in. Cannot create another account while logged in.")
                        continue
                    else:
                        # extract username and then send the correctly formatted request
                        # to the server and get its response
                        username = args[1]
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            # if successful, set the params for this client
                            self.uuid = ord(response)
                            self.username = username
                            print("Status " + str(status) + ": " + "Created account " + username)
                        else:
                            print("Status " + str(status) + ": " + "Username already exists. Pick a different one.")
                # logging in
                elif opcode == "2":
                    if len(args) < 3:
                        print("Incorrect parameters: correct form is 2|[username]|[pwd]")
                    elif self.login:
                        # do not allow re-logging in or logging into another account
                        # while logged in
                        print("Already logged in. Cannot login again or to another account.")
                        continue
                    else:
                        username = args[1]
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            # set username, uuid, and login 
                            if self.username is None:
                                self.username = username
                            if self.uuid is None:
                                self.uuid = int(response)
                            self.login = True
                            print("Status " + str(status) + ": " + "Logged into account")
                        elif status == 1:
                            print("Status " + str(status) + ": " + "Incorrect username.")
                        elif status == 2:
                            print("Status " + str(status) + ": " + "Already logged in.")
                        elif status == 3:
                            print("Status " + str(status) + ": " + "Incorrect password.")
                        else:
                            print("Status " + str(status) + ": " + "Unable to login")
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
                            print("Status " + str(status) + ": " + "Delivered message to " + to_user)
                        elif status == 1:
                            print("Status " + str(status) + ": " + "Could not deliver to " + to_user + ". Check if this username exists")
                        elif status == 2:
                            print("Status " + str(status) + ": " + "Message was too long. Keep messages under 280 characters.")
                        else:
                            print("Status " + str(status) + ": " + "Unable to send message")
                elif opcode == "4":
                    if not self.login:
                        print("Must be logged in to perform this action")
                    else:
                        status, response = self.send_and_get_response(ans + "|" + str(self.uuid))
                        if status == 0:
                            print("Status " + str(status) + ": " + "Retrieved all history for " + self.username)
                        elif status == 1:
                            print("Status " + str(status) + ": " + "No unread messages")
                        else:
                            print("Status " + str(status) + ": " + "Unable to retrieve history")
                elif opcode == "5":
                    if len(args) < 2:
                        print("Incorrect parameters: correct form is 5|[regex_wildcard]")
                    else:
                        status, response = self.send_and_get_response(ans)
                        if status == 0:
                            print("Status " + str(status) + ": " + "Found all matching users")
                        elif status == 1:
                            print("Status " + str(status) + ": " + "No matching users")
                        else:
                            print("Status " + str(status) + ": " + "Unable to retrieve matching users")
                elif opcode == "6":
                    if not self.login:
                        print("Must be logged in to perform this action")
                    else:
                        status, response = self.send_and_get_response(ans + "|" + self.username)
                        if status == 0:
                            self.login = False
                            self.username = None
                            self.uuid = None
                            print("Status " + str(status) + ": " + "Your account has been deleted.")
                        else:
                            print ("Status " + str(status) + ": " + "Unable to delete account.")
                else:
                    print("Invalid opcode. 1 = create account, 2 = login, 3 = send, 4 = fetch, 5 = search, 6 = delete")
                continue
        # close the connection
        self.socket.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 2048
    chat_client = ChatClient(HOST, PORT)
    chat_client.connect()
    chat_client.run_client()
    


