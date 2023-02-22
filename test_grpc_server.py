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

    def test_server_create_account(self):
        self.cleanTable()
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            response = stub.server_create_account(pb2.User(username='divya', password='test'))
            self.assertEqual(response.username, 'divya')
    
            response = stub.server_create_account(pb2.User(username='kat', password='test'))
            self.assertEqual(response.username, 'kat')

            #response = stub.server_create_account(pb2.User(username='divya', password=''))
            #self.assertEqual(response.username, '')
    
    def test_server_login(self):
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            response = stub.server_login(pb2.User(username='test', password='test'))
            self.assertEqual(response.username, '')

            response = stub.server_login(pb2.User(username='divya', password='test'))
            self.assertEqual(response.username, 'divya')

    def test_server_send_chat(self):
        self.cleanTable()
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            setup = stub.server_create_account(pb2.User(username='divya', password='test'))
            response = stub.server_send_chat(pb2.Chat(send_name='divya', receive_name='divya', message='hello'))
            self.assertEqual(response.err_msg, 'success')
    
    def test_server_logout(self):
        self.cleanTable()
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            setup = stub.server_create_account(pb2.User(username='divya', password='test'))
            response = stub.server_logout(pb2.User(username='divya'))
            self.assertEqual(response.login_status, 0)
    
    def test_server_get_chat(self):
        self.cleanTable()
        self.test_server_send_chat()
        with grpc.insecure_channel(f'localhost:{self.port}') as channel:
            stub = pb2_grpc.ChatBotStub(channel)
            response = stub.server_get_chat([pb2.User(username='divya')])
            self.assertEqual(response.send_name, 'divya')


if __name__ == "__main__":
    t = ChatServerTest()
    t.setUp()
    t.test_server_create_account()
    print("success of acc creation")
    t.test_server_login()
    print("success of acc login")
    t.test_server_send_chat()
    print("success of send message")
    t.test_server_logout()
    print("success logout")
    t.tearDown()

