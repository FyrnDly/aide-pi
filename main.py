import os
import serial
import time
import ArducamDepthCamera as ac
from datetime import datetime as dt
from dotenv import load_dotenv
import logging

from module.connectDb import ConnectFirebase
from module.controller import navigation_robot
from module.navigation import AgentModel

# Add Log Info
logging.basicConfig(filename='output.log', level=logging.INFO)
logging.info("Mulai Program")

# Initialize camera
cam = ac.ArducamCamera()
if cam.open(ac.TOFConnect.CSI,0) != 0 :
    logging.info("initialization failed")
if cam.start(ac.TOFOutput.DEPTH) != 0 :
    logging.info("Failed to start camera")

# Initialize Coms Serial
while True:
    try:
        ser = serial.Serial('/dev/ttyUSB0',9600)
        logging.info(f"Terhubung Arduino")
        break
    except Exception as e:
        logging.info(f"Gagal Terhubung Arduino Error: {str(e)}")

# Initialize RL agent
agent = AgentModel(comSerial=ser)
  
if __name__ == "__main__":
    try:
        # Load Dependency on .env
        load_dotenv()

        # Config firebase
        url_firebase = os.getenv('URL_FIREBASE', None)
        path_file_cred = os.getenv('CRED_PATH', None)
        app_fb = ConnectFirebase(path_file_cred, url_firebase)
        try:
            # Connect Firebase
            app_fb.get_connect()

            # Get Schedule Operations
            schedule = app_fb.get_schedule()
            hour_schedule = schedule.keys()
        except Exception as e:
            # Default Schedule
            schedule = {'08:00': '15'}
            hour_schedule = schedule.keys()
            logging.info(f'Errors: {str(e)}')
        # Robot Running
        while True:
            # Initialize Current Time
            time_zone = dt.now()
            hour = time_zone.strftime('%H:%M')
            second = time_zone.strftime('%S')
            minute = time_zone.strftime('%M')
            
            # Check this time operations
            # Running Robot
            if hour in hour_schedule:
                duration = int(schedule[hour])
                navigation_robot(duration=duration, agentModel=agent, camera=cam)
                logging.info(f'AIDE Berhasil Beroperasi pada jam {hour} selama {duration} detik')
                
            # Check 5 minute every time to update battery status
            # Drop comment if u add status percentage battery
            # if not int(minute)%5:
            #     response = ser.readline().decode().strip()
            #     if response:
            #         try:
            #             battery_value = int(float(response))  
            #             app_fb.update_battery(battery_value)
            #             logging.info(app_fb.get_battery())
            #         except Exception as e:
            #             logging.info(f"Data tidak valid: {str(e)} | {type(response)}")
                        
            # Update Schedule and Try Connect Firebase every hour
            if minute == '5':
                try:
                    # Connect to firebase
                    app_fb.get_connect()
                    # Update status robot connection log
                    app_fb.update_log()
                    # Get Schedule Operations
                    schedule = app_fb.get_schedule()
                    hour_schedule = schedule.keys()
                    logging.info(f'AIDE Berhasil Terhubung dengan Server pada jam {hour}:{minute}')
                    time.sleep(60)
                except Exception as e:
                    logging.info(f'Errors: {str(e)}')                        
    except Exception as e:
        logging.info(f'Errors {str(e)}')
