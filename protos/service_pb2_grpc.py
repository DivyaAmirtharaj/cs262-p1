# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from protos import service_pb2 as protos_dot_service__pb2


class ChatServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.chat_stream = channel.unary_stream(
                '/grpc.ChatServer/chat_stream',
                request_serializer=protos_dot_service__pb2.Empty.SerializeToString,
                response_deserializer=protos_dot_service__pb2.Chat.FromString,
                )
        self.send_chat = channel.unary_unary(
                '/grpc.ChatServer/send_chat',
                request_serializer=protos_dot_service__pb2.Chat.SerializeToString,
                response_deserializer=protos_dot_service__pb2.Empty.FromString,
                )


class ChatServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def chat_stream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def send_chat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'chat_stream': grpc.unary_stream_rpc_method_handler(
                    servicer.chat_stream,
                    request_deserializer=protos_dot_service__pb2.Empty.FromString,
                    response_serializer=protos_dot_service__pb2.Chat.SerializeToString,
            ),
            'send_chat': grpc.unary_unary_rpc_method_handler(
                    servicer.send_chat,
                    request_deserializer=protos_dot_service__pb2.Chat.FromString,
                    response_serializer=protos_dot_service__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def chat_stream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/chat_stream',
            protos_dot_service__pb2.Empty.SerializeToString,
            protos_dot_service__pb2.Chat.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def send_chat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/send_chat',
            protos_dot_service__pb2.Chat.SerializeToString,
            protos_dot_service__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)