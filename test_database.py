from database import Database

db = Database()

def create_add():
    try:
        db.create_table()
        print("Success!")
    except Exception as e:
        print("Failed to create tables")

    try:
        db.add_users("divya", "password", 0)
        print("Success, added user to database!")
    except Exception as e:
        print("Failed to add user")

    try:
        db.add_message(1, 2, "hi kat!")
        print("Success, added message to database!")
    except Exception as e:
        print("Failed to add message")
    
    assert(db.get_username(1) == "divya")
    assert(db.get_uuid("divya") == 1)

def login():
    try:
        db.update_login("divya", "passwor", 1)
        print("Success, logged in this user!")
    except Exception as e:
        print(e)
        print("Failed (correctly) to log in user")
    try:
        db.update_login("divya", "password", 1)
        print("Success, logged in this user!")
    except Exception as e:
        print(e)
        print("Failed to log in user")

    assert(db.is_logged_in("divya") == True)


def clean_tables():
    try:
        db.delete_table()
    except:
        print("Failed to delete tables")

def call():
    username = "divya"
    send_id = 1
    receive_id = 2
    try:
        uuid = db.get_uuid(username)
        print("The uuid for divya is", uuid)
    except:
        print("Failed to get uuid")
    
    try:
        history = db.get_message(send_id, receive_id)
        print(history)
    except:
        print("Failed to get message history")

def wildcard():
    try:
        usernames = db.get_usernames("d[a-z]*")
        print(usernames)
    except:
        print("Did not find usernames")
    
    try:
        usernames = db.get_usernames("l[a-z]*")
        print(usernames)
    except:
        print("(Correctly) did not find usernames")
    
    


clean_tables()
create_add()
login()
call()
wildcard()