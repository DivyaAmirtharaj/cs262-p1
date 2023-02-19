from database import Database

db = Database()

def create_add():
    try:
        db.create_table()
        print("Success!")
    except Exception as e:
        print("Failed to create tables")

    try:
        db.add_users("divya")
        print("Success, added user to database!")
    except Exception as e:
        print("Failed to add user")

    try:
        db.add_message(1, 2, "hi kat!")
        print("Success, added message to database!")
    except Exception as e:
        print("Failed to add message")

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
        db.get_message(send_id, receive_id)
    except:
        print("Failed to get message history")


#clean_tables()
#create_add()
call()