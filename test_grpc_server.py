import unittest
from concurrent import futures
from server import Server
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
import grpc
from database import Database

"""
Unit tests for the gRPC server
"""

class ChatServerTest(unittest.TestCase):
    server_class = Server()
    port = 11912

    def setUp(self):
        address = "localhost"
        port = 11912
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_ChatBotServicer_to_server(Server(), self.server)
        self.server.add_insecure_port("{}:{}".format(address, port))
        self.server.start()
    
    def cleanTable(self):
        self.database = Database()
        self.database.delete_table()
        self.database.create_table()

    def tearDown(self):
        self.server.stop(None)

    def test_server(self):
        self.cleanTable()
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            response = stub.server_create_account(pb2.User(username='divya', password='test'))
            self.assertEqual(response.username, 'divya')
    
            response = stub.server_create_account(pb2.User(username='kat', password='test'))
            self.assertEqual(response.username, 'kat')

            response = stub.server_create_account(pb2.User(username='divya', password='test'))
            self.assertEqual(response.username, '')


if __name__ == "__main__":
    t = ChatServerTest()
    t.setUp()
    t.test_server()
    t.tearDown()

