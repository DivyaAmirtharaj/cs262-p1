import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import sys
import time

address = "localhost"
port = 11912

class Client:

    def __init__(self, user = str):
        self.username = user
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.client_get_message, daemon=True).start()

    def client_send_message(self):
        msg = sys.stdin.readline()
        if msg != "":
            n = pb2.Chat()
            n.username = self.username
            n.message = msg
            print("[{}] {}".format(n.username, n.message))
            self.stub.server_send_chat(n)

    def client_get_message(self):
        # arg is the receiver
        # messages is taken from server_get_chat which returns chat history
        # return all the messages
        pass

if __name__ == '__main__':
    username = None
    while username is None:
        print("What's your username? \n")
        username = input()
    while True:
        c = Client("divya") 
        c.client_send_message()

# c = Client("divya")
#c.send_message()
# time.sleep(64 * 64 * 100)
