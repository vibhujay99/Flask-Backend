import pymongo
import bcrypt

client = pymongo.MongoClient("mongodb+srv://user2:user123@cluster0.2qbtenx.mongodb.net/?retryWrites=true&w=majority")
db = client["E-DERMA"]
users = db["users"]


# Register a new user
def register_user(email, name, mobile_number, password):
    ex_user = users.find_one({"email": email})
    if ex_user is not None:
        raise Exception("Email already registered.")

    ex_mobile = users.find_one({"mobile_number": mobile_number})
    if ex_mobile is not None:
        raise Exception("Mobile number already registered.")
    # hash the pw
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    user_data = {
        "name": name,
        "mobile_number": mobile_number,
        "email": email,
        "password": hashed_password,
    }
    # insert to the db
    user = users.insert_one(user_data)
    if user.inserted_id:
        return user_data
    else:
        return "Error"


# Login user
def login_user(email, pw):
    user = users.find_one({"email": email})
    if user is None:
        raise Exception("Email not found")

    hashed_pw = user["password"]
    if bcrypt.checkpw(pw.encode("utf-8"), hashed_pw):
        return user
    else:
        raise Exception("Incorrect password")
