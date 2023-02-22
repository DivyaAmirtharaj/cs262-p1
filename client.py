import sys
import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import time

class Client:
    """
    Methods to implement a client or user via gRPC.  Clients initialize with an address and port (default to localhost).
    We additionally implement multi-threading and our chat functionality implements continuous listening threads to pull
    data nearly instantly (apart from the defined lag).  The main functionality is defined in run(), and relies on user 
    input for fields such as username, and receiving username via the command line.  Objects are passed to the server
    through predefined shapes as defined in our protos file.
    """
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.channel = grpc.insecure_channel("{}:{}".format(self.address, self.port))
        self.stub = pb2_grpc.ChatBotStub(self.channel)
        self.last_seen = []

    # Client Side User management
    # Creates a new user object and adds information to the database
    def client_create_account(self, username, password):
        acc = pb2.User(username=username, password=password)
        new_account = self.stub.server_create_account(acc)
        if new_account.username == "":
            print("That username is taken, please choose another one")
        return new_account
    
    # Queries database to ensure the username exists, and corresponding password is correct before updating login status
    def client_login(self, username, password):
        n = pb2.User()
        n.username = username
        n.password = password
        val = self.stub.server_login(n)
        if val.username == "":
            return True

    # Verifies that a user is logged in
    def client_check_login_status(self, username):
        user = pb2.Id(username=username)
        status = self.stub.server_check_login_status(user)
        if status.login_status == 1:
            return True
        return False
    
    # Verifies that a user exists in the database by querying its uuid and verifying its existence
    def client_check_user_exists(self, username):
        user = pb2.Id(username=username)
        try:
            query = self.stub.server_check_user_exists(user)
            if query.username == "":
                return True
        except grpc.RpcError as e:
            if e.code() != "OK":
                print("Please start the server first")
                exit()   
        return False

    # Calls server to switch login status value to indicate its logged out before exiting
    def client_logout(self, username):
        user = pb2.Id(username=username)
        status = self.stub.server_logout(user)
        if status.login_status == 0:
            print("Successfully logged out")
            exit()
        else:
            print("Failed to logout")
    
    # Calls server to delete user and all their received messages from server, verifies that user is not in table before exiting
    def client_delete_user(self, username):
        user = pb2.Id(username=username)  
        deleted = self.stub.server_delete_user(user)
        if deleted.username == "":
            print("Successfully deleted user")
            exit()
        else:
            print("Failed to delete user")  

    # Client Side Chatting Management
    # Wild card function: gets all the usernames that match regex pattern
    def client_get_user_list(self, pattern):
        regpattern = pb2.Id(username=pattern)
        try:
            user_list = self.stub.server_get_user_list(regpattern)
        except Exception as e:
            print("No users were found with this pattern")
            return []
        return user_list
    
    # Send messages (messages will be queued and displayed later if a user doesn't have the right chat opened)
    def client_send_message(self, username, receive_name, msg):
        message = msg
        if msg != "":
            m = pb2.Chat()
            m.send_name = username
            m.receive_name = receive_name
            m.message = message
            #print("[{}] {}".format(username, m.message))
            return self.stub.server_send_chat(m)

    # Prints unread messages from the database, and displays message history upon first login
    def client_get_message(self, username, receive_name):
        n = pb2.Id()
        n.username = username
        messages = self.stub.server_get_chat(n)
        for m in messages:
            if (m.receive_name == username) and (m.send_name == receive_name) and (m.msgid not in self.last_seen):
                print("[{}] {}".format(m.send_name, m.message))
                self.last_seen.append(m.msgid)
        return [pb2.Chat(m.send_name, m.receive_name, m.msg, m.msgid) for m in messages]

    # Creates and reads a constant stream of messages to continue refreshing client_get_message
    def stream_messages(self, username, receive_name, event, delay = 2):
        while True:
            time.sleep(delay)
            if username is None:
                continue
            while not event.is_set():
                self.client_get_message(username, receive_name)


    def run(self):
       
        # Prompts user to either create a new account or log in
        account_status = input("Please select: \n1) Create account \n2) Login \n")
        while account_status not in ("1", "2", ":exit"):
            account_status = input("Please select only these options: \n1) Create account \n2) Login \n")
        
        # Exit command to quit program
        if account_status == ":exit":
            exit()
       
        # Create account, users will be prompted until the enter a unique username
        elif account_status == "1":
            print("Please create a new username and password!")
            username = input("Username: ")
            while self.client_check_user_exists(username) == False:
                print("That username is taken, please choose another")
                username = input("Username: ")
            password = input("Password: ")
            self.client_create_account(username, password)
        
        # Login
        elif account_status == "2":
            username = input("Username: ")
            while self.client_check_user_exists(username) == True:
                print("That username doesn't exist, try again")
                username = input("Username: ")
            # Checks if a user is already logged in, and if so exits
            if self.client_check_login_status(username):
                print("This user is already logged in, you can only login from one place at a time.")
                exit()
            password = input("Password: ")
            while self.client_login(username, password) == True:
                print("Your password is incorrect, try again")
                password = input("Password: ")

        # Available options once you login: wildcard, chat/ view chat history with a user, logout, delete user, quit (automatically logs you out)
        while True:
            action = input("\nWelcome {}!  Choose one of the following: \n1) Find users \n2) Chat \n3) Logout \n4) Delete account\n".format(username))
            while action not in ("1", "2", "3", "4", ":exit"):
                action = input("Please select only these options: \n1) Find users \n2) Send message \n3) Logout \n4) Delete account")
            
            # Exit command to quit program
            if action == ":exit":
                self.client_logout(username)

            # Wildcard (user searching)
            elif action == "1":
                pattern = input("Please enter the regex pattern for the users you are searching for: ")
                users = self.client_get_user_list(pattern)
                if users:
                    print("Users matching this pattern:")
                    print(users.username)
            
            # Send message to a specific user & load the message history they sent
            elif action == "2":
                print("Welcome {}!  Who would you like to message/ view messages from?".format(username))
                receive_name = input("Recipient: ")
                new_user = self.client_check_user_exists(receive_name)
                if new_user == True:
                    print("That user doesn't exist")
                    self.client_logout(username)
                    break

                stop_event = threading.Event()
                while True:
                    # Runs the task of continously (with a 2 second lag) fetching messages from a specific user to a specific user
                    thread = threading.Thread(target=self.stream_messages, args=(username, receive_name, stop_event, ), daemon=True)
                    thread.start()
                    msg_len = False
                    msg = input()
                    while msg_len is False:
                        if len(msg) > 280 or len(msg) < 1:
                            print("Please enter a non-empty message that is 280 characters or less")
                            msg = input("Message: ")
                        else:
                            msg_len = True
                    if msg == ":exit":
                        # quits thread if the user leaves the chat, messages will be loaded when the user comes back
                        stop_event.set()
                        break
                    else:
                        # sends message
                        self.client_send_message(username, receive_name, msg)
            
            # Log out of account
            elif action == "3":
                self.client_logout(username)
            
            # Delete account
            elif action == "4":
                self.client_delete_user(username)

if __name__ == '__main__':
    address = "localhost"
    port = 11912
    c = Client(address, port)
    c.run()