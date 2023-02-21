from general_server import ChatServer

HOST, PORT = "localhost", 2048
test_server = ChatServer(HOST, PORT)

def test_create_account():
    success, uuid = test_server.create_account("divya", "password")
    assert(success == True)
    assert(uuid == 1)

    success, uuid = test_server.create_account("divya", "password")
    assert(success == False)
    assert(uuid == -1)

    success, uuid = test_server.create_account("kat", "password")
    assert(success == True)
    assert(uuid == 2)

def test_check_user_in_db():
    username = "divya"
    success = test_server.check_user_in_db(username)
    assert(success == True)

    fake_username = "divyaa"
    success = test_server.check_user_in_db(fake_username)
    assert(success == False)

def test_login():
    success, uuid_or_status = test_server.login("divya", "pwd", None)
    assert(success == False)
    assert(uuid_or_status == 3)

    success, uuid_or_status = test_server.login("katt", "pwd", None)
    assert(success == False)
    assert(uuid_or_status == 1)

    success, uuid_or_status = test_server.login("divya", "password", None)
    assert(success == True)
    assert(uuid_or_status == 1)

    success, uuid_or_status = test_server.login("divya", "password", None)
    assert(success == False)
    assert(uuid_or_status == 2)

def test_check_deleted_sender():
    send_uuid = 1
    send_user = "divya"
    rcv_uuid = 2
    rcv_user = "kat"
    try:
        test_server.db.add_message(1, 2, "hi!")
    except:
        print("Could not add message")
    
    try:
        test_server.db.delete_user("divya")
    except:
        print("Could not delete user")

    history = test_server.db.get_all_history(rcv_uuid)

    checked_history = test_server.check_history_for_deleted_sender(history)
    print(checked_history)

    assert(len(checked_history) == 1)

if __name__ == "__main__":
    test_create_account()
    test_check_user_in_db()
    test_login()
    test_check_deleted_sender()


