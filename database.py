import sqlite3

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
                receive_id integer,
                message text
            );
        """)
        con.commit()
    
    @thread_db
    def add_message(self, con, cur, send_id, receive_id, message):
        # insert messages into database for a sender and a receiver
        print(message)
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
        try:
            cur.execute("""
                INSERT INTO messages (msgid, send_id, receive_id, message)
                    VALUES (?, ?, ?, ?)
            """, [latest + 1, send_id, receive_id, message])
        except Exception as e:
            print(e)
        con.commit()

    @thread_db
    def get_message(self, con, cur, send_id, receive_id):
        # given a receiver_id, and the sender_id get the message history between the two users
        try:
            cur.execute("""
                SELECT msgid, send_id, receive_id, message 
                FROM messages
                WHERE (send_id = ?) AND (receive_id = ?)
            """, [send_id, receive_id])
            rows = cur.fetchall()
        except Exception as e:
            print(e)
        
        if rows is None:
            print("No message history")
            raise Exception
        return rows

    @thread_db
    def get_username(self, con, cur, uuid):
        try:
            cur.execute("""
                SELECT username FROM users WHERE (uuid = ?)
            """, [uuid])
        except Exception as e:
            print(e)
    
    @thread_db
    def get_uuid(self, con, cur, username):
        # returns the uuid for a certain user
        cur.execute("""
            SELECT uuid FROM users WHERE username = ?
        """, [username])
        val = cur.fetchone()
        if val is None:
            raise Exception("No user found")
        return val[0]

    @thread_db
    def get_usernames(self, con, cur, pattern):
        # given some pattern, get all the usernames that contain it
        pass

    @thread_db
    def add_users(self, con, cur, username):
        cur.execute("""
            SELECT uuid FROM users ORDER BY uuid DESC LIMIT 1
        """)
        latest = cur.fetchone()
        if latest is None:
            latest = 0
        else:
            latest = latest[0]

        # add a new user to the database with a unique uuid
        cur.execute("""
            INSERT INTO users (uuid, username)
                VALUES (?, ?)
        """, [latest + 1, username])

        con.commit()
    
    @thread_db
    def delete_table(self, con, cur):
        cur.execute("DROP table IF EXISTS messages")
        cur.execute("DROP table IF EXISTS users")
        con.commit()