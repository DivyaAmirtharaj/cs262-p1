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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                msgid integer PRIMARY KEY,
                send_id integer,
                to_id integer,
                message text
            );
        """)
        con.commit()
