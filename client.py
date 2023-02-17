import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import sys
import time

address = "localhost"
port = 11912

class Client:

    def __init__(self, user: str):
        self.username = user
        #channel = grpc.insecure_channel('localhost:11912', options=(('grpc.enable_http_proxy', 0),))
        channel = grpc.insecure_channel('localhost:11912')
        self.stub = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.__get_message, daemon=True).start()

    def send_message(self):
        # send messages to server
        msg = sys.stdin.readline()
        if msg != "":
            n = pb2.Chat()
            n.username = self.username
            n.message = msg
            print("[{}] {}".format(n.username, n.message))
            self.stub.send_chat(n)

    def __get_message(self):
        for c in self.stub.send_chat(pb2.Empty()):
            print("S[{}] {}".format(c.name, c.message))


if __name__ == '__main__':
    username = None
    while username is None:
        print("What's your username? \n")
        username = input()
    c = Client(username) 
    c.send_message()
    time.sleep(100*64*64)

# c = Client("divya")
#c.send_message()
# time.sleep(64 * 64 * 100)
