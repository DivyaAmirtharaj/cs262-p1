import sqlite3
import re
import random

MAX_MESSAGE_LEN = 280

def thread_db(fn):
    def set_up(self, *args, **kwargs):
        con = sqlite3.connect("chat.db")
        cur = con.cursor()
        con.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)
        thread_cur = fn(self, con, cur, *args, **kwargs)
        con.close()
        return thread_cur
    return set_up

class Database(object):
    """
    Implements all the database functionalities necessary for both the general server and grpc server.  
    This includes function to create tables, add and fetch data, and delete information.
    Additionally, the database is threadsafe and allows for simulataneously editing and data retrieval.
    """
    def __init__(self) -> None:
        pass
    
    # Called upon initialization of the server to create a new table to store unique user info, as well as messages
    @thread_db
    def create_table(self, con, cur):
        # create user table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uuid integer PRIMARY KEY,
                username text UNIQUE,
                password text,
                login_status integer
            );
        """)
        # create a messages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                msgid integer PRIMARY KEY,
                send_id integer,
                receive_id integer,
                message text
            );
        """)
        con.commit()
    
    # Called upon initialization of the server to clear messages/ users from previous instances.  Each initialization of
    # the server clears all stored data
    @thread_db
    def delete_table(self, con, cur):
        cur.execute("DROP table IF EXISTS messages")
        cur.execute("DROP table IF EXISTS users")
        con.commit()
    
    # Username/ password from client is passed to the server and added to the database after generating a random uuid
    @thread_db
    def add_users(self, con, cur, username, password, login_status):
        # Random generation of uuid for thread safety
        uuid = random.randint(1, 2**20)
        # Update login status if successful
        cur.execute("""
            INSERT INTO users (uuid, username, password, login_status)
                VALUES (?, ?, ?, ?)
        """, [uuid, username, password, login_status])
        con.commit()
    
    # Used to verify login credentials, queries the password and username from the database before allowing login
    @thread_db
    def verify_username_password(self, con, cur, username):
        try:
            cur.execute("""
                SELECT username, password FROM users WHERE (username = ?)
            """, [username])
        except Exception as e:
            print(e)
        user = cur.fetchone()
        if user is None:
            raise Exception("No user exists with this name")
        return user

    # Pulls the unique id for each username during message sending/ receiving
    @thread_db
    def get_uuid(self, con, cur, username):
        # Given the username, it returns the uuid
        cur.execute("""
            SELECT uuid FROM users WHERE username = ?
        """, [username])
        val = cur.fetchone()
        if val is None:
            # Raise exception if no user is found in the database
            raise Exception("No user found for this username")
        return val[0]
    
    # Pulls the username from the unique id, used primarily for formatting and user comfort when reading messages
    @thread_db
    def get_username(self, con, cur, uuid):
        try:
            cur.execute("""
                SELECT username FROM users WHERE (uuid = ?)
            """, [uuid])
        except Exception as e:
            print(e)
        
        user = cur.fetchone()
        if user is None:
            # Raises exception if there is no user under the particular uuid in the database
            raise Exception("No user found for this uuid")
        return user[0]

    # Query for the wildcard function, and pulls every username that matches the provided regex pattern
    @thread_db
    def get_usernames(self, con, cur, pattern):
        try:
            cur.execute("""
                SELECT username FROM users WHERE username REGEXP ?
            """, [pattern])
        except Exception as e:
            print(e)
        rows = cur.fetchall()
        if rows is None or len(rows) == 0:
            raise Exception("No users found for this query")
        usernames = [row[0] for row in rows]
        return usernames

    # Queries the login status for a user from the users table after every log-in status change to determine success
    # and to prevent duplicate logins
    @thread_db
    def is_logged_in(self, con, cur, username):
        try:
            cur.execute("""SELECT login_status FROM users WHERE username = ? """, [username])
        except Exception as e:
            print(e)
        status = cur.fetchone()
        if status is None:
            return 0
        return status[0]
    
    # Updates login_status for a user if successful upon login (correct username and password)
    @thread_db
    def update_login(self, con, cur, username, password, new_login_status):
        # Multithreading + threadsafe database prevent data races and database locking
        cur.execute("""
                SELECT username FROM users WHERE username = ? AND password = ?
            """, [username, password])
        user = cur.fetchone()
        if user is None:
            raise Exception("Wrong password")
        try: 
            cur.execute("""
                    UPDATE users SET login_status = ? WHERE username = ? AND password = ?
                """, [new_login_status, username, password])
        except Exception as e:
            print(e)
        con.commit()

    # Change login_status to logged out, used during both unintentional and intentional logouts
    # Useful when clients have died to prevent getting locked out from an account since duplicate login is banned
    @thread_db
    def force_logout(self, con, cur, username):
        cur.execute("""
                    UPDATE users SET login_status = 0 WHERE username = ?
                """, [username])
        con.commit()
    
    # Deletes user from all user table, and removes all the messages sent to them
    @thread_db
    def delete_user(self, con, cur, username):
        """
        Delete a user and all of the messages that a user has received.
        """
        uuid = self.get_uuid(username)
        cur.execute("""
                    DELETE FROM users WHERE (username = ?)
                """, [username])
        # Only received messages are deleted, whereas in our custom protocol users can still see messages sent by 
        # deleted users.
        cur.execute("""
                    DELETE FROM messages WHERE (receive_id = ?)
                """, [uuid])
        con.commit()

    # Adds messages sent from the clients into the database.  Names the messages by pulling the most recent entry
    # in the database and adding 1 to create a unique message id.
    @thread_db
    def add_message(self, con, cur, send_id, receive_id, message):
        # Verifies that length of the message is within the acceptable size (256 characters)
        if len(message) > MAX_MESSAGE_LEN:
            raise Exception("Messages must be less than 256 characters")
        
        # Selects the most recent message
        cur.execute("""
            SELECT msgid FROM messages ORDER BY msgid DESC LIMIT 1
        """)
        latest = cur.fetchone()
        if latest is None:
            latest = 0
        else:
            # Identify the latest message id (most recent message)
            latest = latest[0]
        try:
            cur.execute("""
                INSERT INTO messages (msgid, send_id, receive_id, message)
                    VALUES (?, ?, ?, ?)
            """, [latest + 1, send_id, receive_id, message])
        except Exception as e:
            print(e)
        con.commit()

    # Called by the message stream in the grpc client/ server and queries all message history.  We use checkpoints
    # to identify which messages in history have already been sent and which should be queued.
    @thread_db
    def get_message(self, con, cur, receive_id):
        # Given a receiver_id, and the sender_id get the message history between the two users
        cur.execute("""
            SELECT msgid, send_id, receive_id, message 
            FROM messages
            WHERE (receive_id = ?)
            ORDER BY msgid ASC
        """, [receive_id])
        rows = cur.fetchall()
        if rows is None or len(rows) == 0:
            raise Exception("No message history")
        history = []
        for row in rows:
            cur.execute("SELECT username FROM users WHERE (uuid = ?)", [row[1]])
            send_name = cur.fetchone()
            if send_name is None:
                raise Exception("Sender doesn't exist")
            cur.execute("SELECT username FROM users WHERE (uuid = ?)", [row[2]])
            receive_name = cur.fetchone()
            if receive_name is None:
                raise Exception("Receiver doesn't exist")
            #history.append({"send_name": send_name[0], "receive_name": receive_name[0], "message": row[3]})
            history.append({"msgid": row[0], "send_name": send_name[0], "receive_name": receive_name[0], "message": row[3]})
        return history
    
    # Pulled by general client/ server to get full message history
    @thread_db
    def get_all_history(self, con, cur, receive_id):
        # Given a receiver_id, and the sender_id get the message history between the two users
        try:
            cur.execute("""
                SELECT msgid, send_id, receive_id, message 
                FROM messages
                WHERE (receive_id = ?)
                ORDER BY msgid ASC
            """, [receive_id])
            rows = cur.fetchall()
        except Exception as e:
            print(e)
        
        history = []
        if rows is None or len(rows) == 0:
            print("No message history")
            raise Exception
        for row in rows:
            history.append({'send_id': row[1], 'message': row[3]})
        return history

    # Deletes seen messages from the database to prevent duplicate views
    @thread_db
    def delete_history_for_receiver(self, con, cur, receive_id):
        cur.execute("""
            DELETE FROM messages WHERE (receive_id = ?)
        """, [receive_id])
        con.commit()
