from concurrent import futures
import grpc
import time
import protos.service_pb2_grpc as pb2_grpc
import protos.service_pb2 as pb2
from database import Database

def list_to_protobuf(tpe):
    def wrap(f):
        def wrapped(self, request, context, *args, **kwargs):
            ret = f(self, request, context, *args, **kwargs)
            assert isinstance(ret, list)
            for r in ret:
                yield tpe(**r)
        wrapped.__name__ = f.__name__
        return wrapped
    return wrap

class Server(pb2_grpc.ChatBotServicer):
    """
    Implements functionalities of a server for a client/server grpc chat app.
    Receives objects from client (as defined in service.proto) and interfaces with
    the database to store and query data.  The server and database are multi-threaded
    and support constant streaming of data to the client.
    """
    def __init__(self):
        # initialize database, ensure it's clean and build it again
        self.database = Database()
        self.database.delete_table()
        self.database.create_table()

    # Server Side User management
    # Creates a new user from the username and password provided
    def server_create_account(self, request, context):
        username = request.username
        password = request.password
        login_status = 1
        try:
            self.database.add_users(username, password, login_status)
        except Exception as e:
            print(e)
            return pb2.User(uuid=0, username="")
        return pb2.User(username=username) 

    # Changes login_status if password and username are correct
    def server_login(self, request, context):
        username = request.username
        password = request.password
        try:
            val = self.database.verify_username_password(username)
            if val is None:
                return pb2.User(username="")
        except Exception as e:
            print(e)
        
        if (val[0] == username and val[1] == password):
            print("Correct username and password, logging in!")
            new_login_status = 1
            try:
                self.database.update_login(username, password, new_login_status)
            except Exception as e:
                print(e)
                return pb2.User(uuid=0, username="")
            return pb2.User(username=username)
        return pb2.User(username="")

    # Verifies what the login_status of a user is-- prevents duplicate logins
    def server_check_login_status(self, request, context):
        username = request.username
        status = self.database.is_logged_in(username)
        return pb2.User(login_status=status)
    
    # Queries the uuid of a user to ensure it exists in the table
    def server_check_user_exists(self, request, context):
        username = request.username
        try:
            uuid = self.database.get_uuid(username)
        except:
            return pb2.User(username="")
        if uuid != None:
            return pb2.User(username=username)
        return pb2.User(username="")

    # Switches logout status to 0 and queries to make sure logout was successful
    def server_logout(self, request, context):
        username = request.username
        try:
            self.database.force_logout(username)
        except Exception as e:
            print(e)
        status = self.database.is_logged_in(username)
        return pb2.User(login_status=status)

    # Deletes user from USERS table as well as all their received messages
    def server_delete_user(self, request, context):
        username = request.username
        try:
            self.database.delete_user(username)
        except Exception as e:
            print(e)
        try:
            uuid = self.database.get_uuid(username)
        except Exception as e:
            print("Account was successfully deleted")
            return pb2.User(username="")
        return pb2.User(username=username)

    # Server Side Chatting Management
    # Wild card function that queries all potential matching usernames from database
    def server_get_user_list(self, request, context):
        pattern = request.username
        try:
            users = self.database.get_usernames(pattern)
        except Exception as e:
            print(e)
            return pb2.Userlist(username=[])
        return pb2.Userlist(username=users)

    # Adds a sent message to the database and returns success
    def server_send_chat(self, request: pb2.Chat, context):
        send_id = self.database.get_uuid(request.send_name)
        receive_id = self.database.get_uuid(request.receive_name)
        message = request.message
        try:
            self.database.add_message(send_id, receive_id, message)
        except Exception as e:
            print(e)
            return pb2.Outcome(err_type=1, err_msg=e)
        return pb2.Outcome(err_type=0, err_msg="success")
    
    # Streams chat history from database back to the client.
    @list_to_protobuf(pb2.Chat)
    def server_get_chat(self, request, context):
        receive_id = self.database.get_uuid(request.username)
        try:
            messages = self.database.get_message(receive_id)
        except Exception as e:
            return []
        return messages

if __name__ == '__main__':
    address = "localhost"
    port = 11912
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    pb2_grpc.add_ChatBotServicer_to_server(Server(), server)  # register the server to gRPC
    print('Server is listening!')
    server.add_insecure_port("{}:{}".format(address, port))
    server.start()
    while True:
        time.sleep(64 * 64 * 100)