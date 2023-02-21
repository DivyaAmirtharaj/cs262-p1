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
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
    
    def client_get_message(self, username):
        n = pb2.Id()
        n.username = username
        messages = self.stub.server_get_chat(n)
        for m in messages:
            print("R[{}] {}".format(m.send_name, m.message))  # debugging statement
        return [pb2.Chat(m.send_name, m.receive_name, m.msg) for m in messages]

    # User management
    def client_create_account(self, username, password):
        acc = pb2.User(username=username, password=password)
        new_account = self.stub.server_create_account(acc)
        if new_account.username == "":
            print("That username is taken, please choose another one")
        return new_account

    # Chatting functionality
    def client_send_message(self, username, receive_name):
        threading.Thread(target=self.client_get_message(username),
                                 daemon=True).start()
        msg = sys.stdin.readline()
        if msg != "":
            m = pb2.Chat()
            m.send_name = username
            m.receive_name = receive_name
            m.message = msg
            print("[{}] {}".format(username, m.message))
        return self.stub.server_send_chat(m)

    def run(self):
        # login/ create new account
        account_status = input("Are you a new user, y/n? \n")
        if account_status == "y":
            print("Please create a new username and password! \n")
            username = input("Username: ")
            password = input("Password: ")
            self.client_create_account(username, password)
        elif account_status == "n":
            # login function
            pass
        else:
            # raise exception
            pass

        # send message
        try:
            threading.Thread(target=self.client_get_message(username), daemon=True).start()
        except Exception as e:
            print(e)
        print("Welcome {}!  Who would you like to message?".format(username))
        receive_name = input()
        while True:
            self.client_send_message(username, receive_name)

if __name__ == '__main__':
    c = Client()
    c.run()