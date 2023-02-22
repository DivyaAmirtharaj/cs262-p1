from general_server import ChatServer
"""
Unit tests for the non-gRPC server only
"""

HOST, PORT = "localhost", 2048
test_server = ChatServer(HOST, PORT)

def test_create_account():
    """
    Tests normal/duplicate account creation
    """
    # create account 1 (expected successful)
    success, uuid = test_server.create_account("divya", "password", None)
    assert(success == True)

    # try to recreate account 1 (expected unsuccessful)
    success, uuid = test_server.create_account("divya", "password", None)
    assert(success == False)
    assert(uuid == -1)

    # create account 2 (expected successful)
    success, uuid = test_server.create_account("kat", "password", None)
    assert(success == True)

def test_check_user_in_db():
    """
    Tests wheher a username is/isn't in the database
    """
    # look for username (expected successful)
    username = "divya"
    success = test_server.check_user_in_db(username)
    assert(success == True)

    # look for wrong username (expected successful)
    fake_username = "divyaa"
    success = test_server.check_user_in_db(fake_username)
    assert(success == False)

def test_login():
    """
    Tests logging into correct/incorrect accounts multiple times
    """

    # wrong password
    success, uuid_or_status = test_server.login("divya", "pwd", None)
    assert(success == False)
    assert(uuid_or_status == 3)

    # nonexistent user
    success, uuid_or_status = test_server.login("katt", "password", None)
    assert(success == False)
    assert(uuid_or_status == 1)

    # correct login
    success, uuid_or_status = test_server.login("divya", "password", None)
    assert(success == True)

    # tries to login twice
    success, uuid_or_status = test_server.login("divya", "password", None)
    assert(success == False)
    assert(uuid_or_status == 2)

def test_check_deleted_sender():
    """
    Tests that users can be deleted without deleting the messages
    that they have sent
    """
    send_user = "divya"
    send_uuid = test_server.db.get_uuid(send_user)
    rcv_user = "kat"
    rcv_uuid = test_server.db.get_uuid(rcv_user)

    # add a message from user 1 to 2
    try:
        test_server.db.add_message(send_uuid, rcv_uuid, "hi!")
    except:
        print("Could not add message")
    
    # delete user 1
    try:
        test_server.db.delete_user(send_user)
    except:
        print("Could not delete user")

    # retrieve messages for user 2
    history = test_server.db.get_all_history(rcv_uuid)

    checked_history = test_server.check_history_for_deleted_sender(history)
    # output should say "Deleted:[message]"
    print(checked_history)

    # check that messages still exist for user 2, even though
    # user 1 was deleted
    assert(checked_history[0] == "Deleted:hi!")
    assert(len(checked_history) == 1)

def run_all_tests_in_order():
    """
    Runs all the tests in the order they are meant to be in.
    """
    # must always be first
    test_create_account()
    test_check_user_in_db()
    test_login()
    # must log in before performing this test
    test_check_deleted_sender()
    print("Passed tests!")

if __name__ == "__main__":
    run_all_tests_in_order()

