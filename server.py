from concurrent import futures

import grpc
import time

import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2


class Server(pb2_grpc.ChatBotServicer):

    def __init__(self):
        self.chats = []

    def get_chat(self, request_iterator, context):
        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = self.chats[last_message]
                last_message += 1
                yield n
    
    def send_chat(self, request: pb2.Chat, context):
        print("[{}] {}".format(request.username, request.message))
        self.chats.append(request)
        return pb2.Empty()

if __name__ == '__main__':
    port = 11921
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    pb2_grpc.add_ChatBotServicer_to_server(Server(), server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('localhost:11912')
    server.start()
    while True:
        time.sleep(64 * 64 * 100)