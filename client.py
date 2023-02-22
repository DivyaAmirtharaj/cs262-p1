import sys
import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import time

address = "localhost"
port = 11912

class Client:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(self.channel)
        self.last_seen = []

    def client_get_user_list(self, pattern):
        regpattern = pb2.Id(username=pattern)
        try:
            user_list = self.stub.server_get_user_list(regpattern)
        except Exception as e:
            print("No users were found with this pattern")
            return []
        return user_list

    def client_login(self, username, password):
        n = pb2.User()
        n.username = username
        n.password = password
        val = self.stub.server_login(n)
        if val.username == "":
            return True

    def client_check_user_exists(self, username):
        user = pb2.Id(username=username)
        try:
            query = self.stub.server_check_user_exists(user)
            if query.username == "":
                return True
        except Exception as e:
            print(e)
        return False

    def client_check_login_status(self, username):
        user = pb2.Id(username=username)
        status = self.stub.server_check_login_status(user)
        if status.login_status == 1:
            return True
        return False
    
    def client_delete_user(self, username):
        user = pb2.Id(username=username)  
        deleted = self.stub.server_delete_user(user)
        if deleted.username == "":
            print("Successfully deleted user")
            exit()
        else:
            print("Failed to delete user")  
    
    def client_logout(self, username):
        user = pb2.Id(username=username)
        status = self.stub.server_logout(user)
        if status.login_status == 0:
            print("Successfully logged out")
            exit()
        else:
            print("Failed to logout")

    def client_get_message(self, username, receive_name):
        n = pb2.Id()
        n.username = username
        messages = self.stub.server_get_chat(n)
        for m in messages:
            if (m.receive_name == username) and (m.send_name == receive_name) and (m.msgid not in self.last_seen):
                print("[{}] {}".format(m.send_name, m.message))
                self.last_seen.append(m.msgid)
        return [pb2.Chat(m.send_name, m.receive_name, m.msg, m.msgid) for m in messages]

    # User management
    def client_create_account(self, username, password):
        acc = pb2.User(username=username, password=password)
        new_account = self.stub.server_create_account(acc)
        if new_account.username == "":
            print("That username is taken, please choose another one")
        return new_account
    
    # Chatting functionality
    def client_send_message(self, username, receive_name):
        msg = sys.stdin.readline()
        if msg != "":
            m = pb2.Chat()
            m.send_name = username
            m.receive_name = receive_name
            m.message = msg
            #print("[{}] {}".format(username, m.message))
            return self.stub.server_send_chat(m)

    def poll_for_messages(self, username, receive_name, delay = 2):
        while True:
            time.sleep(delay)
            if username is None:
                continue
            msgs = self.client_get_message(username, receive_name)


    def run(self):
        # Todo: verify server is connected
        # Todo: force logout if client crashes
       
        # login/ create new account
        account_status = input("Please select: \n1) Create account \n2) Login \n")
        while account_status not in ("1", "2"):
            account_status = input("Please select only these options: \n1) Create account \n2) Login \n")
        
        # Create account
        if account_status == "1":
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

        # Available options once you login
        while True:
            action = input("\nWelcome {}!  Choose one of the following: \n1) Find users \n2) Chat \n3) Logout \n4) Delete account\n".format(username))
            while action not in ("1", "2", "3", "4"):
                action = input("Please select only these options: \n1) Find users \n2) Send message \n3) Logout \n4) Delete account")
            
            # Wildcard (user searching)
            if action == "1":
                pattern = input("Please enter the regex pattern for the users you are searching for: ")
                users = self.client_get_user_list(pattern)
                if users:
                    print("Users matching this pattern:")
                    print(users.username)
            
            # Send message to a specific user & load the message history they sent
            elif action == "2":
                print("Welcome {}!  Who would you like to message/ view messages from?".format(username))
                receive_name = input("Recipient: ")
                # Todo: check if the user exists
                chatting = True
                while chatting == True:
                    threading.Thread(target=self.poll_for_messages, args=(username, receive_name, ), daemon=True).start()
                    self.client_send_message(username, receive_name)
                    chatting = False
            
            # Log out of account
            elif action == "3":
                self.client_logout(username)
            
            # Delete account
            elif action == "4":
                self.client_delete_user(username)

if __name__ == '__main__':
    c = Client()
    c.run()