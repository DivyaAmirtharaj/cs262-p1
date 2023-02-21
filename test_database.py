from database import Database

db = Database()

# Tests creation and addition of users
def test_create_add():
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
        db.add_users("kat", "password", 0)
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

# Tests logging in and out
def test_login_and_out():
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

    try:
        db.force_logout("divya")
    except Exception as e:
        print(e)
        print("Failed to log out user")

    assert(db.is_logged_in("divya") == False)

    try:
        db.update_login("divya", "password", 1)
        print("Success, logged in this user!")
    except Exception as e:
        print(e)
        print("Failed to log in user")
    
    assert(db.is_logged_in("divya") == True)

    try:
        db.update_login("divya", "password", 0)
        print("Success, logged out this user!")
    except Exception as e:
        print(e)
        print("Failed to log out user")
    
    assert(db.is_logged_in("divya") == False)

# Tests cleaning tables
def test_clean_tables():
    try:
        db.delete_table()
    except:
        print("Failed to delete tables")

def test_get_message():
    username = "divya"
    send_id = 1
    receive_id = 2
    try:
        uuid = db.get_uuid(username)
        print("The uuid for divya is", uuid)
    except:
        print("Failed to get uuid")
    
    assert(uuid == 1)
    
    try:
        history = db.get_message(send_id, receive_id)
        print(history)
    except:
        print("Failed to get message history")

def test_get_history():
    username = "divya"
    uuid = db.get_uuid(username)
    send_username = "kat"
    send_uuid = db.get_uuid(send_username)
    try:
        db.add_message(send_uuid, uuid, "hi divya!")
        db.add_message(send_uuid, uuid, ":)")
        print("Success, added messages to database!")
    except:
        print("Failed to add message")
    
    try:
        history = db.get_all_history(uuid)
        print("Got history " + str(history))
    except:
        print("Failed to get message history")
    
    assert(len(history) == 2)

    try:
        db.delete_history_for_receiver(uuid)
        print("Success")
    except:
        print("Failed to delete history")
    
    try:
        history = db.get_all_history(send_uuid)
        print("Got history " + str(history))
    except:
        print("Failed to get message history")
    
    assert(len(history) == 1)

    try:
        history = db.get_all_history(uuid)
        print(history)
    except:
        print("(Correctly) did not find message history")

def test_wildcard():
    try:
        usernames = db.get_usernames("d[a-z]*")
        print(usernames)
    except:
        print("Did not find usernames")
    
    assert(len(usernames) == 1)
    
    try:
        usernames = db.get_usernames("l[a-z]*")
        print(usernames)
    except:
        print("(Correctly) did not find usernames")
    
    try:
        usernames = db.get_usernames(".*")
        print(usernames)
    except:
        print("Did not find usernames")
    
    assert(len(usernames) == 2)

def test_deletion():
    username = "divya"
    uuid = db.get_uuid(username)
    send_username = "kat"
    send_uuid = db.get_uuid(send_username)

    try:
        db.add_message(send_uuid, uuid, "hi divya!")
        db.add_message(send_uuid, uuid, ":)")
        print("Success, added messages to database!")
    except Exception as e:
        print("Failed to add message")

    try:
        db.delete_user("divya")
    except:
        print("Did not find user")
    
    try:
        usernames = db.get_usernames("divya")
    except:
        print("(Correctly) did not find usernames")
    
    try:
        usernames = db.get_usernames(".*")
    except:
        print("Did not find usernames")

    assert(len(usernames) == 1)
    
    try:
        history = db.get_all_history(username)
    except:
        print("(Correctly) did not find any messages")

    
    
if __name__ == "__main__":
    test_clean_tables()
    test_create_add()
    test_login_and_out()
    test_get_message()
    test_get_history()
    test_wildcard()
    test_deletion()