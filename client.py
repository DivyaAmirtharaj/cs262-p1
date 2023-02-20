import sys
import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
from database import Database

address = "localhost"
port = 11912

class Client:
    def __init__(self, user, password, login_status):
        self.username = user
        self.password = password
        self.login_status = login_status
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.client_get_message, daemon=True).start()
        self.database = Database()

    # User management
    def client_create_account(self):
        acc = pb2.User(username=self.username, password=self.password, login_status=0)
        new_account = self.stub.server_create_account(acc)
        return new_account

    # Chatting functionality
    def client_send_message(self):
        msg = sys.stdin.readline()
        uuid = 3
        print(username)
        if msg != "":
            n = pb2.Chat()
            n.send_id = uuid
            n.message = msg
            print("[{}] {}".format(self.username, n.message))
            self.stub.server_send_chat(n)

    def client_get_message(self):
        # query the message history from the database
        pass

if __name__ == '__main__':
    print("Are you a new user, y/n? \n")
    account_status = input()
    if account_status == "y":
        print("Please create a new username and password! \n")
        print("Username: ")
        username = input()
        print("Password: ")
        password = input()
        c = Client(username, password, login_status=0)
        c.client_create_account()

    else:
        print("Please enter your username and password! \n")
        print("Username: ")
        username = input()
        print("Password: ")
        password = input()

