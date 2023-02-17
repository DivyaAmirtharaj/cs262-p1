import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import sys
import time

address = "localhost"
port = 11912

class Client:
    def __init__(self, user: str) -> None:
        self.username = user
        channel = grpc.insecure_channel('localhost:11912', options=(('grpc.enable_http_proxy', 0),))
        self.stub = pb2_grpc.ChatBotStub(channel)

    def send_message(self):
        # send messages to server
        msg = sys.stdin.readline()
        n = pb2.Chat()
        n.username = self.username
        n.message = msg
        print(type(n))
        self.stub.send_chat(n)

c = Client("divya")
c.send_message()
time.sleep(64 * 64 * 100)
