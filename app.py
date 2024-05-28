import os
from flask import Flask, jsonify, request
from module.connectDb import ConnectFirebase

app = Flask(__name__)

# Connect to firebase
url_firebase = os.getenv('URL_FIREBASE', None)
path_file_cred = os.getenv('CRED_PATH', None)
fb = ConnectFirebase(path_file_cred, url_firebase)
fb.get_connect()

@app.route("/", methods=['GET'])
def ReturnJSON():
    # Get Schedule Operations
    schedule = fb.get_schedule()
    battery = fb.get_battery()
    # JSON Respone
    data = {
        'Jadwal dan Durasi Operasi': schedule,
        'Baterai' : battery,
    }
    return jsonify(data)

@app.route("/battery",methods=["POST"])
def UpdateBattery():
    battery_input = int(request.form['battery'])
    old_battery = fb.get_battery()
    fb.update_battery(battery_input)
    battery = fb.get_battery()
    data = {
        'baterai sebelum' : old_battery,
        'baterai sekarang' : battery
    }
    return jsonify(data)
    

if __name__ =='__main__':
    app.run(debug=True)