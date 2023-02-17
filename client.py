import threading
import grpc
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2

address = "localhost"
port = 11912

class Client:
    def __init__(self) -> None:
        channel = grpc.insecure_channel(address + ":" + str(port))
        self.connection = pb2_grpc.ChatBotStub(channel)
        threading.Thread(target=self.__get_message, daemon=True).start()

    def send_message(self, event):
        message = "hello"
        if message != '':
            n = pb2.Chat() 
            n.username = self.username
            n.msg = message  
            print("S[{}] {}".format(n.username, n.msg))  
            self.connection.send_chat(n)  

    def __get_message(self):
        pass