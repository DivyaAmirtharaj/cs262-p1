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
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.client_get_message, daemon=True).start()
        self.database = Database()

    # User management
    def client_create_account(self, password):
        acc = pb2.User(username=self.username, password=password, login_status=self.login_status)
        new_account = self.stub.server_create_account(acc)
        return new_account

    # Chatting functionality
    def client_send_message(self, receive_id):
        msg = sys.stdin.readline()
        send_uuid = self.database.get_uuid(self.username)
        receive_uuid = self.database.get_uuid(receive_id)
        if msg != "":
            n = pb2.Chat()
            n.send_id = send_uuid
            n.receive_id = receive_uuid
            n.message = msg
            print("[{}] {}".format(self.username, n.message))
            self.stub.server_send_chat(n)

    def client_get_message(self):
        # query the message history from the database
        pass
    
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
        to_username = input()
        self.client_send_message(to_username)

if __name__ == '__main__':
    c = Client()
    c.run()