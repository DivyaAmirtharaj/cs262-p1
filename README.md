# CS262 Wire Protocol Assignment 1

This is a simple, client-server chat application built using sockets and gRPC. It runs on python3. 

Installation:

`pip install sqlite3`
`python -m pip install grpcio`
`python -m pip install grpcio-tools`

## Wire Protocol

First, we describe the wire protocol design part of the assignment. 

### Usage
#### Non-gRPC
In order to run the non-gRPC version of this chat application, run the following to start the server:

`python3 general_server.py`

Open separate windows to create clients:

`python3 general_client.py`

The client gives commands to the server through a command-line text input interface. Commands are formatted as `[opcode]|[arg1][arg2]...`, where opcodes are as follows: 1 = account creation, 2 = login, 3 = message another user, 4 = get message history that was sent offline, 5 = search users by text wldcard, and 6 = delete account.

Some commands can only be used when logged in or with certain arguments. Invald input will be expressed to the client.

#### gRPC
In order to run the gRPC version of this chat application, run the following to start the server:
`python3 server.py`

Open separate windows to create clients:
`python3 client.py`

The client will prompt you for each action via the command-line text input interface.  Upon creation of the client, it will prompt you to type either `1, 2, or ":exit"` which correspond to account_creation, or account_login, or an exit from the client.  Both login commands will prompt you to type in a username or password.  Upon successful account initialization, it will prompt users to again type either `1, 2, 3, 4, or ":exit"`, where 1 = search users by wildcard, 2 = open messaging with another user (send and receive any queued messages, and view message history), 3 = logout, 4 = delete account, and full exit.  We wait until successful user initialization since these functions all require the user to be logged in.  In order to exit a chat thread with a user, users can type `":exit` to return to the command menu.  Logout and account deletion will terminate the client process.

### Wire Protocol and Overall Design

Our server utilizes sqlite3 to store information about both users and messages. Messages that were sent offline are stored in a table in the server-side database, while messages that are sent to an online user are delivered immediately. The two tables are linked through a uuid, which is generated randomly for each user. We assume that the server does not die, so the database is reinitialized whenever the server restarts.

In addition to the above format for input, our wire protocol/design has several other important features:

* Client-side input is taken in the form `[opcode]|[arg1][arg2]...`.
* Input is only checked for the correct number of arguments and for the barrier of login status on the client side. All other checking is done once commands are received by the server socket.
* The maximum message length for either server or client is 280. This includes getting message history or querying usernames (the results are truncated by the server).
* Any messages from server to client are packed as follows: `[status code (chr)][message length (chr)][message type (string char "S" or "C")][message]`
    * The "message type" char determines if the message being sent is a chat (to be displayed directly) or a server response (confirming that the command has succeeded). These are treated differently by the client.
* Any client-to-client messages are automatically sent as `[username]:[message]`. This is performed by the client and server and requires no separate user intervention.
* Client death is treated as logout.
* Clients can only log in to one account at a time, and accounts can only be logged into by one client.

More information can be found in our engineering notebook.

## gRPC

The gRPC version of this chat app uses the same database schema to store users and messages, and thus much of the same server side functionality.  Similar to the wire procotol implementation, we do a majority of our checking on the server side (verifying the existence of a username, verifying correct login, verifying server connection, etc.) with just message length, login status, and correct CLI inputs checked in the client side.

General features:
* Users are forced to choose a unique username in order to create an account.  This is also enforced within the database to ensure that there are no duplicate usernames or uuids stored
* Clients can only log in to one account at a time, and accounts can only be logged into by one client.
* Users can only perform message sending/ queuing, user search, log-out, and account deletion once they are already logged in so these functions are locked until account initialization is performed
* The maximum message length for either server or client is 280. This includes getting message history or querying usernames (the results are truncated by the server).
* When a user opens a chat thread with another user, we automatically open a continuous listening thread specific to the client and the recipient.  This will allow you to receive and send messages in real time.  When a user exits a specific chat thread, then all messages sent from the recipient of that chat thread will be treated as queued messages, and upon the next time the user opens that particular message thread, chat history and the queued messages will be delivered.  This same logic applies for all messages that are sent to a user when the user is logged out.  In order to view a conversation and the queued messages, the user must open that specific chat thread.
* Any client-to-client messages are automatically sent as `[username]:[message]`. This is performed by the client and server and requires no separate user intervention.
* Client death is treated as logout
* If a client does not find a server connection then it will terminate

Continous Listening:
We set up a stream to continuously pull messages sent to a user from a receiver and display or queue them.  We do this by running a thread within a ```while True``` loop which can affect performance.  We try and maintain performance by closing each thread however when a client is not within a certain message thread (actively chatting with another user) and reopen it to display queued messages and deliver messages when the user opens the message thread again.  Clients thus receive messages instantly, but there is a potential performance tradeoff when chat history becomes very large and/or the number of clients becomes large.





