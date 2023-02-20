from concurrent import futures
import grpc
import time
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
from database import Database

class Server(pb2_grpc.ChatBotServicer):

    def __init__(self):
        self.database = Database()
        self.username = ""
        self.login_status = 0

    # User management
    def server_create_account(self, request, context):
        # add check here to make sure it's a unique username
        self.username = request.username
        password = request.password
        self.login_status = request.login_status
        self.database.add_users(self.username, password, self.login_status)
        uuid = self.database.get_uuid(self.username)
        return pb2.User(uuid=uuid, username=self.username, password=password, login_status=self.login_status)
    
    def server_login(self, request, context, username, password):
        # update login status if successful sign in
        pass

    # Chatting functionality
    def server_send_chat(self, request: pb2.Chat, context):
        try:
            receive_id = request.receive_id
            send_id = request.send_id
            message = request.message
            self.database.add_message(send_id, receive_id, message)
        except Exception as e:
            return pb2.Outcome(err_type=1, err_msg=e)
        return pb2.Outcome(err_type=0, err_msg="success")
    
    def server_get_chat(self, request, context):
        # try:
            # get messages from database (based on user id)
        # except Exception as e:
            # return []
        #return messages
        pass



if __name__ == '__main__':
    port = 11921
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    pb2_grpc.add_ChatBotServicer_to_server(Server(), server)  # register the server to gRPC
    print('Starting server. Listening...')
    server.add_insecure_port('localhost:11912')
    server.start()
    while True:
        time.sleep(64 * 64 * 100)