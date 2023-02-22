from general_client import ChatClient
import time
import random
import threading

HOST, PORT = "localhost", 2048

def test_account_creation_and_login():
    """
    Always call this first, or the other tests may not work.

    Creates 2 clients and 2 users. Tests incorrect login info
    and re-logging in
    """
    # create two clients
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    status1, response1 = client1.send_and_get_response("1|kz|pass")
    status2, response2 = client2.send_and_get_response("1|kz|newpass")
    assert(status2 == 1)
    status2, response2 = client2.send_and_get_response("1|da|pass")

    assert(status1 == 0)
    assert(status2 == 0)

    # login to account 1 with wrong password
    status1, response1 = client1.send_and_get_response("2|kz|psss")
    assert(status1 == 3)
    # login with wrong username
    status1, response1 = client1.send_and_get_response("2|kzz|pass")
    assert(status1 == 1)
    # login to account 2 correctly
    status2, response2 = client2.send_and_get_response("2|da|pass")
    assert(status2 == 0)
    # attempt to login to account 2 again
    status2, response2 = client2.send_and_get_response("2|da|pass")
    assert(status2 == 2)
    # attempt to login to account 2 again with different client
    status1, response1 = client1.send_and_get_response("2|da|pass")
    assert(status1 == 2)

    print("PASSED ACCOUNT CREATION TEST")

    client1.socket.close()
    client2.socket.close()
    time.sleep(3)

def test_send_message():
    """
    Creates two clients and logs them into the two accounts created above.
    Sends a short message, a long message (<= 280 char), and a too-long message
    (> 280 char).
    """
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    # login to two accounts correctly
    status1, response1 = client1.send_and_get_response("2|kz|pass")
    assert(status1 == 0)
    client1.uuid = int(response1)
    status2, response2 = client2.send_and_get_response("2|da|pass")
    assert(status2 == 0)
    client2.uuid = int(response2)

    # short message
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hello")
    assert(status1 == 0)

    # long message (<= 280 chars)
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":helloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 0)

    # too long message (>= 281 chars)
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 2)

    print("PASSED MESSAGE TEST")
    client1.socket.close()
    client2.socket.close()
    time.sleep(3)


def test_client_death_and_get_history():
    """
    Creates two clients and logs them into the two existing accounts. 
    Has account 2 drop the connection (effectively logging them out).
    Account 1 then sends a message to account 2, and then deletes its account.
    Account 2 logs back in and retrieves history. The history should show
    the message from Account 1, but with the sending username replaced with 
    'Deleted.'
    """
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    # login to two accounts correctly
    status1, response1 = client1.send_and_get_response("2|kz|pass")
    assert(status1 == 0)
    client1.uuid = int(response1)
    status2, response2 = client2.send_and_get_response("2|da|pass")
    assert(status2 == 0)
    client2.uuid = int(response2)

    # account 2 "dies"
    client2.socket.close()

    # send message to offline client
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hello")
    assert(status1 == 0)

    # delete account 1
    status1, response1, client1.send_and_get_response("6|kz")
    assert(status1 == 0)
    client1.socket.close()

    # account 2 revived and logged in
    client2 = ChatClient(HOST, PORT)
    client2.connect()

    status2, response2 = client2.send_and_get_response("2|da|pass")
    client2.uuid = int(response2)
    assert(status2 == 0)

    # get history and make sure that something was sent (status 0)
    # the printout should show 1 message from user 'Deleted'
    status2, response2 = client2.send_and_get_response("4|" + str(client2.uuid))
    assert(status2 == 0)

    # tries to get history again, which should return a status code of 1
    # because history is erased after it has been fetched
    status2, response2 = client2.send_and_get_response("4|" + str(client2.uuid))
    assert(status2 == 1)

    status2, response2 = client2.send_and_get_response("6|da")
    
    client2.socket.close()
    print("PASSED HISTORY GETTING TEST")

def test_multiple_client_creation_and_login():
    """
    Creates 90 clients and has them all create an account and log in,
    sleeping at random intervals between actions and doing so from different threads.
    Every account is differently named, so all should succeed.
    """
    num_clients = 90
    clients = [None] * num_clients
    threads = [None] * num_clients
    creation_statuses = [None] * num_clients
    login_statuses = [None] * num_clients
    delete_statuses = [None] * num_clients

    def create_account(c, i):
        # randomly sleeps, creates account, and logs in: the amount slept is
        # larger if the client thread is called earlier in order to offset
        # the fact that the thread is called earlier
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        creation_status, creation_response = c.send_and_get_response('1|' + str(i) + '|pass')
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        login_status, login_response = c.send_and_get_response('2|' + str(i) + '|pass')
        # record the operation statuses
        creation_statuses[i] = creation_status
        login_statuses[i] = login_status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()

        # create a new thread for each client and call create_account
        threads[i] = threading.Thread(target=create_account, args=(clients[i], i))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    # ensure that all are successful
    assert(sum(creation_statuses) == 0)
    assert(sum(login_statuses) == 0)

    # further ensure that it works by calling the text wildcard
    # and searching for any username
    # ensure that the number of usernames returned in the response is 90
    # (even if the text may be truncated)
    status, response = clients[0].send_and_get_response('5|.*')
    assert(status == 0)
    assert(int(response) == 90)

    # delete all the accounts made
    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|' + str(i))
        delete_statuses[i] = delete_status
    
    # ensure that the deletes were successful
    assert(sum(delete_statuses) == 0)

    # close all connections
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED SIMULTANEOUS ACCOUNT CREATION TEST")

def test_multiple_client_creation_same_username():
    """
    Attempts to create the same account name with 100 clients simultaneously.
    Only one should succeed.
    """
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients

    def create_account(c, i):
        # randomly sleep before trying to create the account, again proportional
        # to i
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        status, response = c.send_and_get_response('1|acc|pass')
        statuses[i] = status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()

        # creates a thread for each client
        threads[i] = threading.Thread(target=create_account, args=(clients[i], i))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    # 1 is the status code for repeated username, so this indicates
    # that all but one account creation failed
    assert(sum(statuses) == num_clients - 1)

    # delete the single created account
    delete_status, delete_response = clients[i].send_and_get_response('6|acc')
    assert(delete_status == 0)
    
    # close all client sockets
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED SIMULTANEOUS SAME-NAME ACCOUNT CREATION")

def test_two_client_messaging():
    """
    Two clients message each other simultaneously 100 times each.
    There should be no dropped messages.
    """
    clients = [None, None]
    threads = [None, None]
    delete_statuses = [None, None]
    num_times = 100
    num_clients = 2
    statuses = {0: [], 1: []}

    def send_msgs(c, i, other, uuid):
        j = 0
        while j < num_times:
            # randomly sleep each time the client is about to send a message
            time.sleep(random.randint(10, 100) * 10 **(-6))
            status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
            statuses[i].append(status)
            j += 1

    for i in range(num_clients):
        # create two clients
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()
        status, response = clients[i].send_and_get_response('1|acc' + str(i) +  "|pass")
        clients[i].uuid = int(response)
        status, response = clients[i].send_and_get_response('2|acc' + str(i) +  "|pass")

    for i in range(num_clients):
        if i == 1:
            other_acc = 0
        else:
            other_acc = 1

        # create a thread for each client
        threads[i] = threading.Thread(target=send_msgs, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    # ensure that all messages went through
    assert(sum(statuses[0]) == 0)
    assert(sum(statuses[1]) == 0)

    # delete the two clients
    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|acc' + str(i))
        delete_statuses[i] = delete_status
    
    assert(sum(delete_statuses) == 0)

    # close sockets
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED 2-CLIENT MESSAGING TEST")

def test_many_client_messaging():
    """
    Has 100 clients each send a message to each other simultaneously.
    There should be no dropped messages.
    """
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients
    delete_statuses = [None] * num_clients

    def send_single_msg(c, i, other, uuid):
        # sleep randomly before sending message
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
        statuses[i] = status

    for i in range(num_clients):
        # create clients
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()
        status, response = clients[i].send_and_get_response('1|acc' + str(i) +  "|pass")
        clients[i].uuid = int(response)
        status, response = clients[i].send_and_get_response('2|acc' + str(i) +  "|pass")

    for i in range(num_clients):
        # randomly pick someone to message and then start a thread
        other_acc = random.randint(0, num_clients - 1)
        threads[i] = threading.Thread(target=send_single_msg, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()

    # ensure that all messages go through
    assert(sum(statuses) == 0)

    # delete all accounts
    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|acc' + str(i))
        delete_statuses[i] = delete_status
    
    assert(sum(delete_statuses) == 0)

    # close all sockets
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)

    print("PASSED MANY-CLIENT MESSAGING TEST")

def test_account_deletion_during_messaging():
    """
    Creates 100 accounts. Odd-numbered accounts delete their accounts, while
    even-numbered accounts send a message to another random account. The only
    failure that should occur is status code 1 (e.g. this user no longer exists)
    """
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients

    def send_single_msg_and_del(c, i, other, uuid):
        # sleep randomly 
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        if i % 2 == 0:
            status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
            # ensure that a message is only not sent if the receiving account
            # already got deleted
            assert(status < 2)
        else:
            status, response = c.send_and_get_response('6|acc' + str(i))
            assert(status == 0)

    for i in range(num_clients):
        # create all accounts
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()
        status, response = clients[i].send_and_get_response('1|acc' + str(i) +  "|pass")
        clients[i].uuid = int(response)
        status, response = clients[i].send_and_get_response('2|acc' + str(i) +  "|pass")

    for i in range(num_clients):
        # randomly pick an account to message and then start thread
        other_acc = random.randint(0, num_clients - 1)
        threads[i] = threading.Thread(target=send_single_msg_and_del, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    # close all sockets
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)

    print("PASSED DELETING WHILE MESSAGING TEST")

if __name__ == "__main__":
    test_account_creation_and_login()
    test_send_message()
    test_client_death_and_get_history()
    test_multiple_client_creation_and_login()
    test_multiple_client_creation_same_username()
    test_two_client_messaging()
    test_many_client_messaging()
    test_account_deletion_during_messaging()




