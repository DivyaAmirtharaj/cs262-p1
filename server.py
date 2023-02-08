# Create a server

import protos.service_pb2 as chat
import protos.service_pb2_grpc as grpc

class Greeter(grpc.GreeterServicer):
    
  def SayHello(self, request, context):
    return chat.HelloReply(message='Hello, %s!' % request.name)