DK Engineering Notebook

Potentially start with gRPCs
Throw exceptions or else

Starting with a gRPC
1. Install gRPC
- Install grpcio (need pip3): python -m pip install grpcio
- Install grpcio tools: python -m pip install grpcio-tools

2. Install Proto: create a proto file to define fixed structure: defined "chat" and "empty" in the .proto file using proto3
- Installation of proto3: brew install protobuf
- Install vscode-proto3 in Marketplace on vscode
- Create a proto file (specify proto3)
- Create a synced, executable proto file: python -m grpc_tools.protoc --proto_path=. protos/service.proto --python_out=. --grpc_python_out=.

GENERAL SERVER-SIDE DESIGN
- use a multithreaded server, with one thread per client
- use a dictionary (potentially hash?) to store users
- use a list (of booleans or usernames) to keep track of who is online --> how do you tell this?
- should probably block while deleting an account

GENERAL CLIENT DESIGN
- client has two threads, one to listen and one to write messages with
- messages deliver immediately when they are online
- messages deliver when "fetched" when they are offline --> is there a risk that you "fill" their buffer with messages when offline? maybe

GENERAL REQUEST DESIGN
- opcode: 1 = register, 2 = login, 3 = send message, 4 = receive messages (?)--> this could solve the issue of how to deliver messages when a user is offline, 5 = list usernames by text wildcard, 6 = delete account
- parameters should be delimited by | (e.g. "1|bob")
- parameters for 1: account name
	- need to reject account if the username already exists
	- return: a key
- parameters for 2: account name
	- need to reject account if the username doesn't already exist, and prompt the user to register
	- return: message that you have logged in, maybe a printout of the client host/port?
- parameters for 3: receiving account name (or key), message to be sent
	- need to reject if the username doesn't exist
	- need to reject if message too long (how long?)
	- need to reject if message empty
	- return: some ack of success
- parameters for 4: none
	- return: buffered up messages
- parameters for 5: a text wildcard
	- need to do input checking here
	- return: list of account names
- parameters for 6: none
	- user should only be able to delete their own account


DESIGN CHOICES
- can do input checking in the server or client side
- handling account deletion --> maybe people get the messages that were sent + some note that deleted user A is now "inactive?"

CASES TO COVER
- general invalid input format (e.g. opcode + params not delimited -- if this is true, we treat the entire thing as an opcode and say that it's invalid, invalid opcode)
	- maybe even check for delimiters to give a more pointed error message
- invalid account names for sending messages/login
- repeat account names for registering
- deleting an account
	- make sure the account info, online list, and account dict is being blocked
	- decide what to do about receiving messages from a deleted account
- make sure that general send/receive works
- make sure that offline send/receive works (command 4 is essentially a fetch command)
- message size (no empty messages, no messages too long)

02/19/2023
- things to note in notebook
    - client side failure
        - if client crashes, consider them logged out and any future messages queued
        - force logout function in database — helps when a client crashes. logs out with only the username, only ever called by server when client crashes
    - login flow
        - block multiple logins of the same user (in the same or different clients)
        - specific status codes for wrong user/pass
    - new database operations
        - force_logout (see above)
        - update_login — for logging in a user
        - is_logged_in — checks login status (mostly for queueing messages)
        - get_all_history — get queued messages
    - new server operations (non-grpc)
        - check_user_in_db: used to verify message sending to valid users, utilizes get_uuid by catching its exception

- things to fix
    - fix message format (for kat)
    - send history as a response, not a message (server and client side)
- things to implement
    - server-side text wildcard (for kat)
    - account deletion
    - modifying get_all_history to clear messages for receive_id whenever called successfully
        - can either be done in method or through a clear_history method
    - write more database tests
    - write normal tests
- things to potentially improve
    - defining exception classes for common errors

