import protos.service_pb2 as chat
import protos.service_pb2_grpc as grpc

class Client:
    def run():
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = grpc.GreeterStub(channel)
            response = stub.SayHello(chat.HelloRequest(name='you'))
            print("Greeter client received: " + response.message)
            response = stub.SayHelloAgain(chat.HelloRequest(name='you'))
            print("Greeter client received: " + response.message)
