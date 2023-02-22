# CS262 Wire Protocol Assignment 1

This is a simple, client-server chat application built using sockets and gRPC. It runs on python3. 

## Wire Protocol

First, we describe the wire protocol design part of the assignment. 

### Usage

In order to run the non-gRPC version of this chat application, run the following to start the server:

`python3 general_server.py`

Open separate windows to create clients:

`python3 general_client.py`

The client gives commands to the server through a command-line text input interface. Commands are formatted as `[opcode]|[arg1][arg2]...`, where opcodes are as follows: 1 = account creation, 2 = login, 3 = message another user, 4 = get message history that was sent offline, 5 = search users by text wldcard, and 6 = delete account.

Some commands can only be used when logged in or with certain arguments. Invald input will be expressed to the client.

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

The gRPC version of this chat app uses the same database schema to store users and messages.

[INSERT MORE HERE]






