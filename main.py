import os
from dotenv import load_dotenv
import numpy as np
from module.connectDb import ConnectFirebase

# Load Dependency on .env
load_dotenv()

# Connect to firebase
url_firebase = os.getenv('URL_FIREBASE', None)
path_file_cred = os.getenv('CRED_PATH', None)
app_fb = ConnectFirebase(path_file_cred, url_firebase)
app_fb.get_connect()

# Test Get battery for firebase
print(app_fb.get_battery())