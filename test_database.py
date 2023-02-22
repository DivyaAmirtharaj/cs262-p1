from database import Database

"""
Tests database functionality alone.
"""

db = Database()

def test_create_add():
    """
    Tests creation and addition of users. Must be called before
    any other test that involve adding or modifying users in the database.
    """

    # create a table
    try:
        db.create_table()
        print("Success!")
    except Exception as e:
        print("Failed to create tables")

    # add user 1
    try:
        db.add_users("divya", "password", 0)
        print("Success, added user to database!")
    except Exception as e:
        print("Failed to add user")

    # add user 2
    try:
        db.add_users("kat", "password", 0)
        print("Success, added user to database!")
    except Exception as e:
        print("Failed to add user")

    # check that get functions work properly 
    assert(db.get_username(db.get_uuid("divya")) == "divya")

    # add a message from user 1 to user 2
    try:
        db.add_message(db.get_uuid("divya"), db.get_uuid("kat"), "hi kat!")
        print("Success, added message to database!")
    except Exception as e:
        print("Failed to add message")
    

def test_login_and_out():
    """
    Tests logging in and out of accounts (correctly/incorrectly)
    """
    # try to log in with wrong password (should fail)
    try:
        db.update_login("divya", "passwor", 1)
        print("Success, logged in this user!")
    except Exception as e:
        print(e)
        print("Failed (correctly) to log in user")
    
    # log in with correct password
    try:
        db.update_login("divya", "password", 1)
        print("Success, logged in this user!")
    except Exception as e:
        print(e)
        print("Failed to log in user")

    # check login status
    assert(db.is_logged_in("divya") == True)

    # ensure that logout works (this method is used by server)
    try:
        db.force_logout("divya")
    except Exception as e:
        print(e)
        print("Failed to log out user")

    # check login status
    assert(db.is_logged_in("divya") == False)

def test_clean_tables():
    """
    Tests cleaning tables. Call this first in order to clean the database
    of any previous changes.
    """
    try:
        db.delete_table()
    except:
        print("Failed to delete tables")

def test_get_message():
    """
    Tests if getting messages for a certain receiver works (gRPC version)
    """
    username = "divya"
    send_id = db.get_uuid(username)
    receive_id = db.get_uuid("kat")
    
    try:
        history = db.get_message(receive_id)
        print(history)
    except:
        print("Failed to get message history")

def test_get_history():
    """
    Tests if getting messages for a certain receiver works
    """
    username = "divya"
    uuid = db.get_uuid(username)
    send_username = "kat"
    send_uuid = db.get_uuid(send_username)

    # add messages from user 2 to user 1
    try:
        db.add_message(send_uuid, uuid, "hi divya!")
        db.add_message(send_uuid, uuid, ":)")
        db.add_message(uuid, send_uuid, "hey!")
        print("Success, added messages to database!")
    except:
        print("Failed to add message")
    
    # get history for user 2 (should contain two messages)
    try:
        history = db.get_all_history(uuid)
        print("Got history " + str(history))
    except:
        print("Failed to get message history")
    
    assert(len(history) == 2)

    # delete history for user 2
    try:
        db.delete_history_for_receiver(uuid)
        print("Success")
    except:
        print("Failed to delete history")
    
    # check that history for user 1 (the sender) still exists
    try:
        history = db.get_all_history(send_uuid)
        print("Got history " + str(history))
    except:
        print("Failed to get message history")
    
    assert(len(history) >= 1)

    # check that history for user 2 no longer exists
    try:
        history = db.get_all_history(uuid)
        print(history)
    except:
        print("(Correctly) did not find message history")

def test_wildcard():
    """
    Check searching by text wildcard (regex).
    """

    # find user 1
    try:
        usernames = db.get_usernames("d[a-z]*")
        print(usernames)
    except:
        print("Did not find usernames")
    
    assert(len(usernames) == 1)
    
    # find a wildcard that does not have any results
    try:
        usernames = db.get_usernames("l[a-z]*")
        print(usernames)
    except:
        print("(Correctly) did not find usernames")
    
    # find a wildcard that includes both usernames
    try:
        usernames = db.get_usernames(".*")
        print(usernames)
    except:
        print("Did not find usernames")
    
    assert(len(usernames) == 2)

def test_deletion():
    """
    Check that a user and their received messages can be properly deleted,
    but their sent messages are not deleted.
    """
    username = "divya"
    uuid = db.get_uuid(username)
    send_username = "kat"
    send_uuid = db.get_uuid(send_username)

    try:
        # send messages from user 2 to user 1
        db.add_message(send_uuid, uuid, "hi divya!")
        db.add_message(send_uuid, uuid, ":)")
        print("Success, added messages to database!")
    except Exception as e:
        print("Failed to add message")

    # delete user 1
    try:
        db.delete_user("divya")
    except:
        print("Did not find user")
    
    # ensure that user 1 is no longer in the user table
    try:
        usernames = db.get_usernames("divya")
    except:
        print("(Correctly) did not find usernames")
    
    # ensure that user 1 can no longer be found through searching
    try:
        usernames = db.get_usernames(".*")
    except:
        print("Did not find usernames")

    assert(len(usernames) == 1)
    
    # try to find all messages received by user 1
    try:
        history = db.get_all_history(uuid)
    except:
        print("(Correctly) did not find any messages")
    
    # find all messages received by user 2
    try:
        history = db.get_all_history(send_uuid)
        print(history)
    except:
        print("Did not find any messages")
    
    assert(len(history) >= 1)

def run_all_tests_in_order():
    """
    Runs all unit tests in the desired order
    """
    # these three tests must occur first in this order
    test_clean_tables()
    test_create_add()
    test_login_and_out()

    test_get_message()
    test_get_history()
    test_wildcard()

    # this test should occur last
    test_deletion()
    print("Passed tests!")
    
    
if __name__ == "__main__":
    run_all_tests_in_order()