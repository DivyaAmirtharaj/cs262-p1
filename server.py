import grpc
from concurrent import futures
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2


class Server(pb2_grpc.ChatBotServicer):
    def __init__(self) -> None:
        self.history = []
        pass
    
    def send_chat(self, request, context):
        print(request)
        return(pb2.Empty())

if __name__ == '__main__':
    port = 11921
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))  # create a gRPC server
    pb2_grpc.add_ChatBotServicer_to_server(Server(), server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('localhost:11912')
    server.start()
    server.wait_for_termination()