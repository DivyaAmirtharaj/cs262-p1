import sys
import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
from database import Database

address = "localhost"
port = 11912

class Client:
    def __init__(self):
        self.username = None
        self.login_status = None
        self.receive_id = None
        self.database = Database()
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
#threading.Thread(target=self.client_get_message(), daemon=True).start()

    # User management
    def client_create_account(self, password):
        acc = pb2.User(username=self.username, password=password, login_status=self.login_status)
        new_account = self.stub.server_create_account(acc)
        return new_account

    # Chatting functionality
    def client_send_message(self):
        msg = sys.stdin.readline()
        send_uuid = self.database.get_uuid(self.username)
        receive_uuid = self.database.get_uuid(self.receive_id)
        if msg != "":
            n = pb2.Chat()
            n.send_id = send_uuid
            n.receive_id = receive_uuid
            n.message = msg
            print("[{}] {}".format(self.username, n.message))
        return self.stub.server_send_chat(n)

    def client_get_message(self):
        send_uuid = self.database.get_uuid(self.username)
        receive_uuid = self.database.get_uuid(self.receive_id)
        req = pb2.Chat()
        req.send_id = send_uuid
        req.receive_id = receive_uuid
        req.message = ""
        print(req)
        print(self.stub.server_get_chat(req))
    
    def run(self):
        # login/ create new account
        print("Are you a new user, y/n? \n")
        account_status = input()
        if account_status == "y":
            print("Please create a new username and password! \n")
            print("Username: ")
            self.username = input()
            print("Password: ")
            password = input()
            self.client_create_account(password)
        elif account_status == "n":
            # login function
            pass
        else:
            # raise exception
            pass

        # send message
        print("Welcome {}!  Who would you like to message?".format(self.username))
        self.receive_id = input()
        while True:
            self.client_send_message()
            self.client_get_message()

if __name__ == '__main__':
    c = Client()
    c.run()