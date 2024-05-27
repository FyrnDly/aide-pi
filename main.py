import os
import serial
import pickle
import time
import numpy as np
import os.path as path
import ArducamDepthCamera as ac
from datetime import datetime as dt
from dotenv import load_dotenv

from module.connectDb import ConnectFirebase
from module.controller import navigation_robot
from module.navigation import PolicyGradientAgent as AgentModel

# Initialize camera
cam = ac.ArducamCamera()
if cam.open(ac.TOFConnect.CSI,0) != 0 :
    print("initialization failed")
if cam.start(ac.TOFOutput.DEPTH) != 0 :
    print("Failed to start camera")

# Initialize RL agent
if path.isfile('model.pkl'):
    with open('model.pkl','rb') as model:
        agent = model
else:
    agent = AgentModel()
  
if __name__ == "__main__":
    try:
        # Load Dependency on .env
        load_dotenv()

        # Connect to firebase
        url_firebase = os.getenv('URL_FIREBASE', None)
        path_file_cred = os.getenv('CRED_PATH', None)
        app_fb = ConnectFirebase(path_file_cred, url_firebase)
        app_fb.get_connect()

        # Get Schedule Operations
        schedule = app_fb.get_schedule()
        hour_schedule = schedule.keys()

        # Initialize Coms Serial
        ser = serial.Serial('COM4',9600)
        while True:
            # Initialize Current Time
            time_zone = dt.now()
            hour = time_zone.strftime('%H:%M')
            second = time_zone.strftime('%S')
            
            # Check this time operations
            # Running Robot
            if hour in hour_schedule:
                duration = int(schedule[hour])
                navigation_robot(duration=duration, agentModel=agent, camera=cam)
                
            # Check 1 minute every time to update battery status
            if second == '10':
                response = ser.readline().decode().strip()
                if response:
                    try:
                        battery_value = int(float(response))  
                        app_fb.update_battery(battery_value)
                        print(app_fb.get_battery())
                    except Exception as e:
                        print(f"Data tidak valid: {str(e)} | {type(response)}")
                        
    except Exception as e:
        print(f'Errors {str(e)}')
