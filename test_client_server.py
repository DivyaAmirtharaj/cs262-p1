from general_client import ChatClient
import time
import random
import threading

HOST, PORT = "localhost", 2048

def test_account_creation_and_login():
    """
    Always call this first, or the other tests may not work
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

    client1.socket.close()
    client2.socket.close()

def test_send_message():
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    # login to two accounts correctly
    status1, response1 = client1.send_and_get_response("2|kz|pass")
    client1.uuid = int(response1)
    status2, response2 = client2.send_and_get_response("2|da|pass")
    client2.uuid = int(response2)

    # short message
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hello")
    assert(status1 == 0)

    # long message (280 chars)
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":helloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 0)

    # too long message (281 chars)
    status1, response1 = client1.send_and_get_response("3|da|" + str(client1.uuid) + ":hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 2)

    client1.socket.close()
    client2.socket.close()


def test_client_death_and_get_history():
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    # login to two accounts correctly
    status1, response1 = client1.send_and_get_response("2|kz|pass")
    status2, response2 = client2.send_and_get_response("2|da|pass")

    # short message
    status1, response1 = client1.send_and_get_response("3|da|1:hello")
    assert(status1 == 0)

    # long message (280 chars)
    status1, response1 = client1.send_and_get_response("3|da|1:hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 0)

    # too long message (281 chars)
    status1, response1 = client1.send_and_get_response("3|da|1:hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 2)

    client1.socket.close()
    client2.socket.close()

def test_wildcard():
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

def test_client_deletion_and_get_history():
    client1 = ChatClient(HOST, PORT)
    client2 = ChatClient(HOST, PORT)
    client1.connect()
    client2.connect()

    # login to two accounts correctly
    status1, response1 = client1.send_and_get_response("2|kz|pass")
    status2, response2 = client2.send_and_get_response("2|da|pass")

    # short message
    status1, response1 = client1.send_and_get_response("3|da|1:hello")
    assert(status1 == 0)

    # long message (280 chars)
    status1, response1 = client1.send_and_get_response("3|da|1:hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    assert(status1 == 0)

    # too long message (281 chars)
    status1, response1 = client1.send_and_get_response("3|da|1:hellooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    print(status1)
    assert(status1 == 2)

    client1.socket.close()
    client2.socket.close()

def test_multiple_client_creation():
    HOST = "localhost"
    PORT = 2048
    num_clients = 100
    clients = [None] * num_clients
    threads = [None] * num_clients
    statuses = [None] * num_clients

    def create_acc(c, i):
        time.sleep(random.randint(10, 100) * 10 **(-9) * (num_clients - i) **3)
        status, response = c.send_and_get_response('1|acc' + str(i) + '|pass')
        statuses[i] = status

    for i in range(num_clients):
        clients[i] = ChatClient(HOST, PORT)
        clients[i].connect()

        threads[i] = threading.Thread(target=create_acc, args=(clients[i], i))
        threads[i].start()
    
    for i in range(num_clients):
        threads[i].join()
    
    assert(sum(statuses) == 0)

    for i in range(num_clients):
        clients[i].socket.close()

    time.sleep(3)


if __name__ == "__main__":
    test_account_creation_and_login()
    test_send_message()

    test_multiple_client_creation()





