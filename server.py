import grpc
from concurrent import futures
import time
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2


class Server(pb2_grpc.ChatBotServicer):
    def __init__(self) -> None:
        pass
    
    def send_chat(self, request: pb2.Chat, context):
        print(print("[{}] {}".format(request.name, request.message)))
        return pb2.Empty()

if __name__ == '__main__':
    port = 7172001
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))  # create a gRPC server
    pb2_grpc.add_ChatBotServicer_to_server(Server, server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)