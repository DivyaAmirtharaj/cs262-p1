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
    def __init__(self) -> None:
        pass
    
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
    
    @thread_db
    def add_message(self, con, cur, send_id, receive_id, message):
        # insert messages into database for a sender and a receiver
        if len(message) > MAX_MESSAGE_LEN:
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
    def get_message(self, con, cur, receive_id):
        # given a receiver_id, and the sender_id get the message history between the two users
        cur.execute("""
            SELECT msgid, send_id, receive_id, message 
            FROM messages
            WHERE (receive_id = ?)
            ORDER BY msgid ASC
        """, [receive_id])
        rows = cur.fetchall()
        if rows is None:
            raise Exception("No message history")
        history = []
        if rows is None or len(rows) == 0:
            raise Exception("No message history")

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
    
    @thread_db
    def get_all_history(self, con, cur, receive_id):
        # given a receiver_id, and the sender_id get the message history between the two users
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
    
    @thread_db
    def pop_message(self, con, cur, receive_id, msgid):
        cur.execute("""
            DELETE FROM messages WHERE (receive_id = ?) and (msgid = msgid)
        """, [receive_id, msgid])
        con.commit()

    @thread_db
    def delete_history_for_receiver(self, con, cur, receive_id):
        cur.execute("""
            DELETE FROM messages WHERE (receive_id = ?)
        """, [receive_id])
        con.commit()

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
            raise Exception("No user found for this uuid")
        return user[0]
    
    @thread_db
    def get_uuid(self, con, cur, username):
        # returns the uuid for a certain user
        cur.execute("""
            SELECT uuid FROM users WHERE username = ?
        """, [username])
        val = cur.fetchone()
        if val is None:
            raise Exception("No user found for this username")
        return val[0]

    @thread_db
    def get_usernames(self, con, cur, pattern):
        # given some pattern, get all the usernames that contain it
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

    @thread_db
    def add_users(self, con, cur, username, password, login_status):
        # cur.execute("""
        #     SELECT uuid FROM users ORDER BY uuid DESC LIMIT 1
        # """)
        # latest = cur.fetchone()
        # if latest is None:
        #     latest = 0
        # else:
        #     latest = latest[0]

        uuid = random.randint(1, 2**20)

        # add a new user to the database with a unique uuid
        cur.execute("""
            INSERT INTO users (uuid, username, password, login_status)
                VALUES (?, ?, ?, ?)
        """, [uuid, username, password, login_status])

        con.commit()
    
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
    
    @thread_db
    def update_login(self, con, cur, username, password, new_login_status):
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

    @thread_db
    def force_logout(self, con, cur, username):
        # useful when a client has died
        cur.execute("""
                    UPDATE users SET login_status = 0 WHERE username = ?
                """, [username])
        con.commit()
    
    @thread_db
    def delete_user(self, con, cur, username):
        """
        Delete a user and all of the messages that a user has received.
        """
        uuid = self.get_uuid(username)
        cur.execute("""
                    DELETE FROM users WHERE (username = ?)
                """, [username])
        cur.execute("""
                    DELETE FROM messages WHERE (receive_id = ?)
                """, [uuid])
        con.commit()

    @thread_db
    def delete_table(self, con, cur):
        cur.execute("DROP table IF EXISTS messages")
        cur.execute("DROP table IF EXISTS users")
        con.commit()