# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from protos import service_pb2 as protos_dot_service__pb2


class ChatBotStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.server_send_chat = channel.unary_unary(
                '/grpc.ChatBot/server_send_chat',
                request_serializer=protos_dot_service__pb2.Chat.SerializeToString,
                response_deserializer=protos_dot_service__pb2.Outcome.FromString,
                )
        self.server_get_chat = channel.unary_unary(
                '/grpc.ChatBot/server_get_chat',
                request_serializer=protos_dot_service__pb2.User.SerializeToString,
                response_deserializer=protos_dot_service__pb2.Chat.FromString,
                )
        self.server_create_account = channel.unary_unary(
                '/grpc.ChatBot/server_create_account',
                request_serializer=protos_dot_service__pb2.User.SerializeToString,
                response_deserializer=protos_dot_service__pb2.User.FromString,
                )


class ChatBotServicer(object):
    """Missing associated documentation comment in .proto file."""

    def server_send_chat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def server_get_chat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def server_create_account(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatBotServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'server_send_chat': grpc.unary_unary_rpc_method_handler(
                    servicer.server_send_chat,
                    request_deserializer=protos_dot_service__pb2.Chat.FromString,
                    response_serializer=protos_dot_service__pb2.Outcome.SerializeToString,
            ),
            'server_get_chat': grpc.unary_unary_rpc_method_handler(
                    servicer.server_get_chat,
                    request_deserializer=protos_dot_service__pb2.User.FromString,
                    response_serializer=protos_dot_service__pb2.Chat.SerializeToString,
            ),
            'server_create_account': grpc.unary_unary_rpc_method_handler(
                    servicer.server_create_account,
                    request_deserializer=protos_dot_service__pb2.User.FromString,
                    response_serializer=protos_dot_service__pb2.User.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.ChatBot', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatBot(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def server_send_chat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatBot/server_send_chat',
            protos_dot_service__pb2.Chat.SerializeToString,
            protos_dot_service__pb2.Outcome.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def server_get_chat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatBot/server_get_chat',
            protos_dot_service__pb2.User.SerializeToString,
            protos_dot_service__pb2.Chat.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def server_create_account(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatBot/server_create_account',
            protos_dot_service__pb2.User.SerializeToString,
            protos_dot_service__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
