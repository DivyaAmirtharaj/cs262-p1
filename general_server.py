import socket
import random
import re
from database import Database

# import thread module
from _thread import *
import threading

MAX_MSG_LEN = 280
LOGGED_IN = 1
LOGGED_OUT = 0
HEADER_LENGTH = 3

class ChatServer:
    """
    Implements the functionalities of a server for a command-line chat app.
    Receives client connections and responds to their requests.
    """
    def __init__(self, host, port):
        """
        Initializes the server host, port, and socket. Also initializes
        storage for client sockets and a database for storing user information
        and message history. Clears the database if it already has values in it.
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_sockets = {}
        self.db = Database()
        self.db.delete_table()
        self.db.create_table()
    
    def check_user_in_db(self, username):
        """
        Checks if a username is in the database by trying to retrieve
        its uuid. If nothing is returned, catch exception and return.

        return: Boolean representng whether the user is in the database
        """
        try: 
            uuid_exists = self.db.get_uuid(username)
        except Exception as e:
            print("Username is invalid")
            print(e)
            return False
        return True

    def send_message(self, sock, message_type, status, message):
        """
        Sends a message to a client socket. Concatenates operation
        status, message length, and message type (chat or server response)
        and sends it to the user.

        return: Boolean representing whether the message was successfully
        sent
        """
        message_len = len(message)
        if message_len > MAX_MSG_LEN:
            # note that messages are in the form [sending_user]:[message]
            # so the number of chars in the [sending_user] username 
            # is considered when finding message length
            print("Message too long")
            return False
        
        to_send = chr(status) + chr(message_len)
        to_send += message_type + message
        print(to_send)

        assert(len(to_send) == HEADER_LENGTH + len(message))
        sock.sendall(to_send.encode('UTF-8'))
        return True

    def send_or_queue_message(self, message, from_id, user_from, user_to_send):
        """
        Sends specifically chat messages to a client socket. Concatenates
        the username of the sender with the message, so that the receiving
        user knows who the message is from. Only sends the message over the
        socket if the receiving user is logged in.

        return: Boolean representing success of the operation, int representing
        status (to be sent to client)
        """
                
        if self.check_user_in_db(user_to_send):
            user_to_send_sock = self.user_sockets[user_to_send]
        else:
            return False, 1

        # check login status of receiving user
        if self.db.is_logged_in(user_to_send):
            cat_message = user_from + ":" + message
            result = self.send_message(user_to_send_sock, "C", 0, cat_message)
            if not result:
                return False, 2
        else:
            # if not logged in, add message the receiving users queue
            receive_id = self.db.get_uuid(user_to_send)
            self.db.add_message(from_id, receive_id, message)
        
        return True, 0
    
    def create_account(self, username, pwd):  
        """
        Attempts to create an account for client with the given username and password.
        Attempts to add this username and password to the database. If
        an exception is raised, the username already exists. Returns the
        UUID (created by the database) of this new user and the status
        of account creation.

        return: Boolean representing success of the operation, int for the UUID (-1
        if the user already exists)
        """
        pwdHash = hash(pwd)
        try:
            self.db.add_users(username, pwdHash, LOGGED_OUT)
        except Exception as e:
            print(e)
            print("Repeat user")
            return False, -1
        
        # this operation will succeed because the user
        # has been added to the database
        uuid = self.db.get_uuid(username)
        # add this new user as a key in the socket dictionary
        self.user_sockets[username] = None
        return True, uuid
        
    def login(self, username, pwd, c):
        """
        Attempts login with the given username and password. Checks if the
        user is already in the database, is already logged in, or if 
        the password is incorrect and returns a status code accordingly.
        If the operation succeeds, store the socket for this user and
        return its UUID to be sent to the client.

        return: Boolean representing success of the operation, int that represents
        the UUID if the operation was successful, or the status code for the exact 
        error that occurred if not
        """
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
        """
        Used by the server to constantly receive from a particular
        client socket. Peeks at a single byte of data first in order
        to determine if the client is still online. If it is, receives
        1024 bytes from the client.

        return: a UTF-8 string containing a request made by the client
        """

        # make sure client is still online
        data = c.recv(1, socket.MSG_PEEK)

        if len(data) == 0:
            # if not, raise an exception to be caught
            # in the main serving loop
            raise Exception("Client died")
        data = c.recv(1024)
        return data
    
    def check_history_for_deleted_sender(self, history):
        """
        Checks a list of chat history messages retrieved from the database
        and replaces the sender with 'deleted' if the sender no longer exists
        in the database. Returns the amended history.

        return: a list of strings that include the changed history
        """
        checked_history = []
        for item in history:
            if "send_id" not in item or "message" not in item:
                continue 
            from_uuid = item["send_id"]
            message = item["message"]
            try:
                user_from = self.db.get_username(from_uuid)
            except Exception as e:
                user_from = "Deleted"
            checked_history.append(user_from + ":" + message)
        
        return checked_history
    
    def pack_arr_as_str(self, arr):
        """
        Takes a list as items and formats them into a string.
        Used for getting message history and searching users.

        return: a string concatenation of all the list items
        """
        return "\n".join([str(item) for item in arr])

    def threaded(self, c):
        """
        Method called by each thread for each client, which receives
        from that client specifically. Constantly receives from the client
        until it dies/is disconnected. Processes the arguments from any client 
        input and sends responses to the client based on whether the requested
        operations finished succesfully.
        """
        while True:
            try:
                data = self.recv_from_socket(c)
            except Exception as e:
                print(e)
                print("Client died")

                # if the client dies, end this loop, log the user out,
                # and reset the socket for the user.
                lost_user = list(self.user_sockets.keys())[list(self.user_sockets.values()).index(c)]
                self.db.force_logout(lost_user)
                self.user_sockets[lost_user] = None
                break

            data_str = data.decode('UTF-8')
            if not data:
                print("No message received")
                break
            print(data_str + "\n")

            # Requests from a client are sent in the form of [opcode]|[arg1]|[arg2]...
            # The format of these requests has already been verified on the client side
            # (e.g. clients cannot send invalid request forms)
            data_list = data_str.split("|")
            opcode = data_list[0]

            print("Opcode: " + str(opcode))

            # checks of argument validity have been done on the client side,
            # so args can be unpacked without fear of error
            # if-elif-else statement that takes care of each possible opcode
            if opcode == "1":
                # create account
                username = str(data_list[1])
                pwd = str(data_list[2])
                
                success, uuid = self.create_account(username, pwd)

                # if successful, return successful response
                # and UUID of new user so it can be stored
                # by the client
                if success:
                    self.send_message(c, "S", 0, chr(uuid))
                else:
                    self.send_message(c, "S", 1, "")
            
            elif opcode == "2":
                # login to account
                username = str(data_list[1])
                pwd = str(data_list[2])
                
                success, uuid_or_status = self.login(username, pwd, c)

                # if successful, return succesful response and UUID
                # of this user, in case the client is logging back
                # in to a preexisting account.
                if success:
                    self.send_message(c, "S", 0, chr(uuid_or_status))
                else:
                    self.send_message(c, "S", uuid_or_status, "")
            
            elif opcode == "3":
                # send message from client A to client B
                user_to_send = str(data_list[1])
                message = str(data_list[2])

                # assume that messages from the client are packaged in the form
                # [uuid of sending user]:[text message].
                message_args = message.split(":")
                from_uuid = int(message_args[0])
                text_message = message_args[1]

                # retrieve the username of the sending user
                try:
                    user_from = self.db.get_username(from_uuid)
                except Exception as e:
                    # if it does not exist, indicate that this user
                    # has been deleted
                    print("User has been deleted")
                    continue

                success, status = self.send_or_queue_message(text_message, from_uuid, user_from, user_to_send)

                self.send_message(c, "S", status, "")

            elif opcode == "4":
                # get history
                uuid = int(data_list[1])

                try:
                    all_history = self.db.get_all_history(uuid)
                except Exception as e:
                    # If there is no new message history,
                    # indicate this to the client
                    print("No history")
                    self.send_message(c, "S", 1, "")
                    continue
                
                all_history = self.check_history_for_deleted_sender(all_history)
                all_history_message = self.pack_arr_as_str(all_history)
                # limit the history to the most recent if total history is
                # over the message length limit
                if len(all_history_message) > MAX_MSG_LEN:
                    all_history_message = all_history_message[-1 * MAX_MSG_LEN:]

                # send history as a chat message
                success = self.send_message(c, "C", 0, all_history_message)

                if success:
                    self.send_message(c, "S", 0, "")
                    self.db.delete_history_for_receiver(uuid)
                else:
                    self.send_message(c, "S", 2, "")
            
            elif opcode == "5":
                # get matching users
                wildcard = str(data_list[1])

                try:
                    matching_users = self.db.get_usernames(wildcard)
                except Exception as e:
                    # if no such users found, indicate
                    # this to the user
                    print("No matching users")
                    self.send_message(c, "S", 1, "")
                    continue
                
                matching_users_message = self.pack_arr_as_str(matching_users)
                # limit the usernames to the first few results if 
                # the total exceeds the maximum message length
                if len(matching_users_message) > MAX_MSG_LEN:
                    matching_users_message = matching_users_message[:MAX_MSG_LEN + 1]
                # send the matching users as a message
                success = self.send_message(c, "C", 0, matching_users_message)
                
                if success:
                    self.send_message(c, "S", 0, "")
                else:
                    self.send_message(c, "S", 2, "")

            else:
                username = str(data_list[1])
                try:
                    self.db.delete_user(username)
                except Exception as e:
                    self.send_message(c, "S", 1, "")
                self.send_message(c, "S", 0, "")
            
        c.close()

    def start_server(self):
        """
        Starts the server by binding its socket to the initialized host/port
        and having it listen. Continuously accept client connections and 
        begin a new thread for receiving from each client whenever a client
        connects.
        """
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