import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import sys
from database import Database

address = "localhost"
port = 11912

class Client:

    def __init__(self, user = str):
        self.username = user
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.client_get_message, daemon=True).start()
        self.database = Database()

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

    def create_user(self, username):
        pass
        

if __name__ == '__main__':
    username = None
    while username is None:
        print("What's your username? \n")
        username = input()
    while True:
        c = Client(username) 
        c.client_send_message()

# c = Client("divya")
#c.send_message()
# time.sleep(64 * 64 * 100)
