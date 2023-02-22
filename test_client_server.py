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
    Has account 2 log out, 
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

    client2.socket.close()

    # send message to offline client
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hello")
    assert(status1 == 0)

    status1, response1, client1.send_and_get_response("6|kz")
    assert(status1 == 0)
    client1.socket.close()

    client2 = ChatClient(HOST, PORT)
    client2.connect()

    status2, response2 = client2.send_and_get_response("2|da|pass")
    client2.uuid = int(response2)
    assert(status2 == 0)

    status2, response2 = client2.send_and_get_response("4|" + str(client2.uuid))
    assert(status2 == 0)

    status2, response2 = client2.send_and_get_response("4|" + str(client2.uuid))
    assert(status2 == 1)
    
    client2.socket.close()
    print("PASSED HISTORY GETTING TEST")

def test_multiple_client_creation_and_login():
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    creation_statuses = [None] * num_clients
    login_statuses = [None] * num_clients
    delete_statuses = [None] * num_clients

    def create_account(c, i):
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        creation_status, creation_response = c.send_and_get_response('1|acc' + str(i) + '|pass')
        login_status, login_response = c.send_and_get_response('2|acc' + str(i) + '|pass')
        creation_statuses[i] = creation_status
        login_statuses[i] = login_status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()

        threads[i] = threading.Thread(target=create_account, args=(clients[i], i))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    assert(sum(creation_statuses) == 0)
    assert(sum(login_statuses) == 0)

    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|acc' + str(i))
        delete_statuses[i] = delete_status
    
    assert(sum(delete_statuses) == 0)

    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED SIMULTANEOUS ACCOUNT CREATION TEST")

def test_multiple_client_creation_same_username():
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients

    def create_account(c, i):
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        status, response = c.send_and_get_response('1|acc|pass')
        statuses[i] = status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()

        threads[i] = threading.Thread(target=create_account, args=(clients[i], i))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    assert(sum(statuses) == num_clients - 1)

    delete_status, delete_response = clients[i].send_and_get_response('6|acc')
    assert(delete_status == 0)
    
    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED SIMULTANEOUS SAME-NAME ACCOUNT CREATION")

def test_two_client_messaging():
    clients = [None, None]
    threads = [None, None]
    delete_statuses = [None, None]
    num_times = 100
    num_clients = 2
    statuses = {0: [], 1: []}

    def send_msgs(c, i, other, uuid):
        j = 0
        while j < num_times:
            time.sleep(random.randint(10, 100) * 10 **(-6))
            status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
            statuses[i].append(status)
            j += 1

    for i in range(num_clients):
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

        threads[i] = threading.Thread(target=send_msgs, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|acc' + str(i))
        delete_statuses[i] = delete_status
    
    assert(sum(delete_statuses) == 0)
    
    assert(sum(statuses[0]) == 0)
    assert(sum(statuses[1]) == 0)

    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)
    print("PASSED 2-CLIENT MESSAGING TEST")

def test_many_client_messaging():
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients
    delete_statuses = [None] * num_clients

    def send_single_msg(c, i, other, uuid):
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
        statuses[i] = status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()
        status, response = clients[i].send_and_get_response('1|acc' + str(i) +  "|pass")
        clients[i].uuid = int(response)
        status, response = clients[i].send_and_get_response('2|acc' + str(i) +  "|pass")

    for i in range(num_clients):
        other_acc = random.randint(0, num_clients - 1)
        threads[i] = threading.Thread(target=send_single_msg, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()

    assert(sum(statuses) == 0)

    for i in range(num_clients):
        delete_status, delete_response = clients[i].send_and_get_response('6|acc' + str(i))
        delete_statuses[i] = delete_status
    
    assert(sum(delete_statuses) == 0)

    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)

    print("PASSED MANY-CLIENT MESSAGING TEST")

def test_account_deletion_during_messaging():
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients

    def send_single_msg_and_del(c, i, other, uuid):
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        if i % 2 == 0:
            status, response = c.send_and_get_response('3|acc' + str(other) + "|" + str(uuid) + ":" + "hi")
        else:
            status, response = c.send_and_get_response('6|acc' + str(other))
        statuses[i] = status
        assert(statuses[i] < 2)

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()
        status, response = clients[i].send_and_get_response('1|acc' + str(i) +  "|pass")
        clients[i].uuid = int(response)
        status, response = clients[i].send_and_get_response('2|acc' + str(i) +  "|pass")

    for i in range(num_clients):
        other_acc = random.randint(0, num_clients - 1)
        threads[i] = threading.Thread(target=send_single_msg_and_del, args=(clients[i], i, other_acc, clients[i].uuid))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
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




