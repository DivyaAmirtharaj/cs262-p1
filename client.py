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
    
    def client_login(self, username, password):
        n = pb2.User()
        n.username = username
        n.password = password
        val = self.stub.server_login(n)
        if val.username == "":
            return True

    def client_check_user_exists(self, username):
        user = pb2.Id(username=username)
        query = self.stub.server_check_user_exists(user)
        if query.username == "":
            return True
        return False

    def client_check_login_status(self, username):
        user = pb2.Id(username=username)
        status = self.stub.server_check_login_status(user)
        if status.login_status == 1:
            return True
        return False
    
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

        # Potential login options
        while True:
            action = input("\nWelcome {}!  Choose one of the following: \n1) Find users \n2) Chat \n3) Logout \n4) Delete account\n".format(username))
            while action not in ("1", "2", "3", "4"):
                action = input("Please select only these options: \n1) Find users \n2) Send message \n3) Logout \n4) Delete account")

            if action == "2":
                # send message
                print("Welcome {}!  Who would you like to message/ view messages from?".format(username))
                receive_name = input()
                chat_open = True
                #threading.Thread(target=self.poll_for_messages, args=(username, ), daemon=True).start()
                while chat_open == True:
                    proc = threading.Thread(target=self.poll_for_messages, args=(username, receive_name, ), daemon=True)
                    proc.start()
                    self.client_send_message(username, receive_name)
                    if input() == ":exit":
                        chat_open = False
            
            elif action == "3":
                print("logout")
            
            elif action == "4":
                print("delete")

if __name__ == '__main__':
    c = Client()
    c.run()