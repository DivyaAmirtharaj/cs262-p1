# DK Engineering Notebook

## Initial Thoughts on gRPC

- Potentially start with gRPCs
- Throw exceptions or else

Starting with a gRPC
1. Install gRPC
- Install grpcio (need pip3): python -m pip install grpcio
- Install grpcio tools: python -m pip install grpcio-tools

2. Install Proto: create a proto file to define fixed structure: defined "chat" and "empty" in the .proto file using proto3
- Installation of proto3: brew install protobuf
- Install vscode-proto3 in Marketplace on vscode
- Create a proto file (specify proto3)
- Create a synced, executable proto file: python -m grpc_tools.protoc --proto_path=. protos/service.proto --python_out=. --grpc_python_out=.

## Initial Thoughts on Wire Protocol
GENERAL SERVER-SIDE DESIGN
- use a multithreaded server, with one thread per client
- use a dictionary (potentially hash?) to store users
- use a list (of booleans or usernames) to keep track of who is online --> how do you tell this?
- deleting an account can cause issues

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

## Initial Design

Started by implementing account creation, login, and messaging (things that don't involve too much storage or storage modification)



USER STORAGE
- for now, just let the server have a username: password dictionary
- server should also store user IDs
- server should store a socket to username or username to socket dictionary
    - let's try socket to username first

ACCOUNT CREATION/LOGIN
- definitely need a password --> should hash the password for security's sake
- check if user is already logged in (in general, not just on this client)
- check if username/password are right

MESSAGING
- just have messages show up for now
- user types in message, client side adds "client uuid:" to the beginning of the message (send uuids for security?)
- then, server maps uuid -> username and sends that to the other client
- what if client dies -> queue the message

general question: where to do input checking? right now, all on the server

## Wire Protocol Phase 1

SENDING (SERVER SIDE)
- need message length and then message so that the client knows how much to receive for (doesn't receive too little or too much)
- should probably have server send responses for confirmation back to the original calling client
    - need a status code (mostly for server confirmation responses)
    - make these show up at the right time?

RECEIVING (CLIENT SIDE)
- unpack the status code and message length
- then, read as many bytes as are in the message
- recv can occur in a bunch of chunks so just keep receiving until you read all the bytes you want

## Wire Protocol Phase 2

SENDING (SERVER SIDE)
- 2 message types: server response and chat
    - chat is displayed immediately to the screen
    - server response is queued up using python Queue --> thread-safe data structure and then popped after the send operation finishes by the client
- encode message length and status code as unicode chars
    - this seems to be buggy, sometimes the unicode char jsut doesn't render

RECEIVING (CLIENT SIDE)
- ideally, we read in X bytes of header
- then, we keep recving according to message length
- should solve any issues of dropped parts of the message

note: unicode char does work (using python func chr) --> can definitely encode our max length of 280. the bug from before was likely due to trying to add the chr to a string. 

## Database + More Design Choices

basic wire protocol is functioning, we discussed using a database and decided on sqlite3 in multithreading mode (we will only have one connection per thread) with two tables

- Decided to have database index by uuid so that the two tables are linked
- database allows addition of new users and messages right now, as well as getting the username and uuid
- working on a method that queues up the history for either a pair of users or for one receiver
    - we decided
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
    - use get_uuid and get_username as checking functions
- new server operations (non-grpc)
    - check_user_in_db: used to verify message sending to valid users, utilizes get_uuid by catching its exception

- things to fix
    - fix message format -- right now, an extra username: is being added somewhere
    - send history as a response, not a message (server and client side) -- want it to display instantly and send a separate response
- things to implement
    - server-side text wildcard
    - database text wildcard
    - account deletion (in database and server)
    - modifying get_all_history to clear messages for receive_id whenever called successfully
        - can either be done in method or through a clear_history method
    - write more database tests
    - write normal tests

What to do with queued messages during account deletion?
- delete the messages received by that account (if any)
- could delete or keep the messages sent
- could add a dummy "deleted user" in the database?

final decision: keep the messages, replace the username of the sender with "deleted" or soemthing like that in the server

## Testing
- wrote tests for the database specifically
    - artificially add users and messages, and then test functionalities like login, logout, and all of the database checking functions
    - decided to throw exceptions when a query to the database returns 0 results (even though the database doesn't)
    - made database a bit safer (throwing some exceptions in checking functions to avoid any issues at runtime)

- server-specific tests
    - testing the few server-side wrapper functions for database functions
    - tested the function for getting history and text wildcard, including with deleting users
    - truncate history and text wildcard to max message length (280)

- concurrency tests
    - things like creating/logging into a lot of accounts from a lot of clients, or sending lots of messages between a couple + many clients
    - also test deleting accounts while they are being messaged
    - realized that our current database UUID was not idempotent -- it was a counter (oops)
        - changed to random int generation
        - also changed general_server to read it in as an int not a single chr (never needed to do that anyway, not sure why I was doing that) so that it can take on larger values
