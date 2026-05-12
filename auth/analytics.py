from auth.config import load_dotenv
from app.master import app
from firebase_admin import credentials, _apps, db
import firebase_admin   

load_dotenv()

def db_ref(path: str):
    return db.reference(path)

def initialize():
    if not _apps:
        try:
            cred = credentials.Certificate(app.config["SERVICE_ACCOUNT_PATH"])
            firebase_admin.initialize_app(
                cred, {"databaseURL": app.config["DATABASE_URL"]}
            )
            print("Initialized firebase..")

        except Exception as e:
            print("failed to connect: ", e)
            exit()

    else:
        print("Initialized already!")

def write(path: str, data: dict):
    ref = db_ref(path)
    try:
        ref.set(data)
        print("write succesful!")

    except Exception as e:
        print("data not set: ", e)

def read(path: str):
    ref = db_ref(path)
    try:
        data = ref.get()
        return data
    except:
        print("read error!")

def update(path: str, data: dict):
    ref = db_ref(path)
    try:
        ref.update(data)
        print("updated succesfully!")
    except:
        print("failed updating!")