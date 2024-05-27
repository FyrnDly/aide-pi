import firebase_admin
from firebase_admin import db
from datetime import datetime as dt

class ConnectFirebase:
    def __init__(self, path_cred, url_firebase):
        self.path_cred = path_cred
        self.url_firebase = url_firebase

    def get_connect(self):
        try:
            cred_obj = firebase_admin.credentials.Certificate(self.path_cred)
            firebase_admin.initialize_app(cred_obj, {'databaseURL': self.url_firebase})
            return f"Berhasil terhubung dengan Firebase!"
        except Exception as e:
            print(f"Gagal terhubung dengan Firebase. Error: {str(e)}")
    
    def get_battery(self):
        ref = db.reference('/battery')
        return ref.get()
    
    def update_battery(self,battery):
        ref = db.reference('/battery')
        try:
            ref.set(battery)
            return f"Berhasil update status battery {self.get_battery()}"
        except Exception as e:
            print(f'Gagal update status battery. Error: {str(e)}')
            
    def get_schedule(self):
        ref = db.reference('/operations').get()
        data = dict()
        for key, value in ref.items():
            data[value['started']] = value['duration']
        return data
    
    def add_pest(sef, hour, pest):
        time = dt.now()
        year, month, day = time.strftime('%Y'), time.strftime('%m'), time.strftime('%d')
        try:
            ref = db.reference(f'/pests/{year}/{month}/')
            ref.child(day).child(hour).set(pest)
            return "Berhasil menambahkan data hama"
        except Exception as e:
            print(f"Gagal menambahkan jumlah hama. Error {str(e)}")
        