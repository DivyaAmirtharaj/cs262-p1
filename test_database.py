from database import Database

db = Database()

try:
    db.create_table()
    print("success!")
except Exception as e:
    print("failed to create tables")


try:
    db.add_users("kat")
    print("success, added user to database!")
except Exception as e:
    print("failed to add user")
