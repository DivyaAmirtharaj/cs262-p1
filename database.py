import sqlite3
import sys

def thread_db(fn):
    def set_up(self, *args, **kwargs):
        con = sqlite3.connect("chat.db")
        cur = con.cursor()
        thread_cur = fn(self, con, cur, *args, **kwargs)
        con.close()
        return thread_cur
    return set_up



class Database(object):
    def __init__(self) -> None:
        pass

    @thread_db
    def create_table(self, con, cur):
        # create user table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uuid integer PRIMARY KEY,
                username text UNIQUE
            );
        """)
        # create a messages table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                msgid integer PRIMARY KEY,
                send_id integer,
                to_id integer,
                message text
            );
        """)
        con.commit()
    
    @thread_db
    def add_message(self, con, cur, send_id, receive_id, message):
        # insert messages into database for a sender and a receiver
        if len(message) > 256:
            raise Exception("Messages must be less than 256 characters")
        
        # selects the most recent message
        cur.execute("""
            SELECT msgid FROM messages ORDER BY msgid DESC LIMIT 1
        """)
        latest = cur.fetchone()
        if latest is None:
            latest = 0
        else:
            # identify the latest message id (most recent message)
            latest = latest[0]
        
        cur.execute("""
            INSERT INTO messages 
                (msgid, send_id, to_id, message)
                VALUES
                (?, ?, ?, ?)
        """,(latest+1, send_id, receive_id, message))

        con.commit()
    
    @thread_db
    def get_message(self, con, cur, send_id, receive_id):
        # given a receiver_id, and the sender_id get the message history between the two users
        pass

    @thread_db
    def get_uuid(self, con, cur, username):
        # given a username, get the associated uuid
        pass
    
    @thread_db
    def get_usernames(self, con, cur, pattern):
        # given some pattern, get all the usernames that contain it
        pass

    @thread_db
    def add_users(self, con, cur, username):
        # given a new username, create a uuid and insert into the table
        pass