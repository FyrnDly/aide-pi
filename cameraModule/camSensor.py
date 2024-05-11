import sys
import cv2
import numpy as np
import ArducamDepthCamera as ac
import serial
import time
from datetime import datetime

# Membuat objek serial untuk komunikasi dengan Arduino
#ser = serial.Serial('/dev/ttyACM0', 9600)

MAX_DISTANCE = 4

# Fungsi untuk memproses frame dan mengembalikan gambar hasil proses
def process_frame(depth_buf: np.ndarray, amplitude_buf: np.ndarray) -> np.ndarray:
    depth_buf = np.nan_to_num(depth_buf)
    amplitude_buf[amplitude_buf<=7] = 0
    amplitude_buf[amplitude_buf>7] = 255
    depth_buf = (1 - (depth_buf/MAX_DISTANCE)) * 255
    depth_buf = np.clip(depth_buf, 0, 255)
    result_frame = depth_buf.astype(np.uint8)  & amplitude_buf.astype(np.uint8)
    return result_frame 

# Kelas untuk menyimpan koordinat persegi yang dipilih oleh pengguna
class UserRect():
    def __init__(self) -> None:
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

selectRect = UserRect()
followRect = UserRect()

# Fungsi callback untuk event mouse
def on_mouse(event, x, y, flags, param):
    global selectRect,followRect
    if event == cv2.EVENT_LBUTTONDOWN:
        pass
    elif event == cv2.EVENT_LBUTTONUP:
        selectRect.start_x = x - 4 if x - 4 > 0 else 0
        selectRect.start_y = y - 4 if y - 4 > 0 else 0
        selectRect.end_x = x + 4 if x + 4 < 240 else 240
        selectRect.end_y=  y + 4 if y + 4 < 180 else 180
    else:
        followRect.start_x = x - 4 if x - 4 > 0 else 0
        followRect.start_y = y - 4 if y - 4 > 0 else 0
        followRect.end_x = x + 4 if x + 4 < 240 else 240
        followRect.end_y = y + 4 if y + 4 < 180 else 180
        
# Kelas menyimpan jarak
class Distance:
    def __init__(self, depth_buf):
        self.depth_buf = depth_buf

    def center(self):
        # Mengambil jarak di posisi tengah frame
        y, x = self.depth_buf.shape[0] // 2, self.depth_buf.shape[1] // 2
        distance = self.depth_buf[y, x] * 100  # Mengubah jarak ke cm
        return distance

    def left(self):
        # Mengambil jarak di posisi kiri frame
        y, x = self.depth_buf.shape[0] // 2, self.depth_buf.shape[1] // 4
        distance = self.depth_buf[y, x] * 100  # Mengubah jarak ke cm
        return distance

    def right(self):
        # Mengambil jarak di posisi kanan frame
        y, x = self.depth_buf.shape[0] // 2, self.depth_buf.shape[1] * 3 // 4
        distance = self.depth_buf[y, x] * 100  # Mengubah jarak ke cm
        return distance

    def rules(self):
        # Mengirim sinyal ke Arduino berdasarkan jarak
        center = self.center()
        left = self.left()
        right = self.right()
        if center > 50:
            #ser.write(b'maju')
            print('maju')
        elif 20 <= center <= 50:
            #ser.write(b'berhenti')
            print('berhenti')
            time.sleep(1)
            if left > right:
                #ser.write(b'kiri')
                print('kiri')
            elif right > left:
                #ser.write(b'kanan')
                print('kanan')
            else:
                #ser.write(b'mundur')
                print('mundur')
        else:
            #ser.write(b'mundur')
            print('mundur')


if __name__ == "__main__":
    cam = ac.ArducamCamera()
    if cam.open(ac.TOFConnect.CSI,0) != 0 :
        print("initialization failed")
    if cam.start(ac.TOFOutput.DEPTH) != 0 :
        print("Failed to start camera")
    cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
    cv2.namedWindow("preview", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("preview",on_mouse)
    
    # Membuat objek VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Mengubah codec menjadi 'mp4v'
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out_raw = cv2.VideoWriter(f'records/raw-{current_time}.mp4', fourcc, 20.0, (1280, 720))  # Mengubah ukuran frame menjadi 720p dan format menjadi .mp4
    out_depth = cv2.VideoWriter(f'records/depth-{current_time}.mp4', fourcc, 20.0, (1280, 720))  # Mengubah ukuran frame menjadi 720p dan format menjadi .mp4

    while True:
        frame = cam.requestFrame(200)
        if frame != None:
            depth_buf = frame.getDepthData()
            amplitude_buf = frame.getAmplitudeData()
            # Raw cam
            cam.releaseFrame(frame)
            amplitude_buf*=(255/1024)
            amplitude_buf = np.clip(amplitude_buf, 0, 255)
            # Depth Cam
            result_image = process_frame(depth_buf,amplitude_buf)
            result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_JET)
            cv2.rectangle(result_image,(selectRect.start_x,selectRect.start_y),(selectRect.end_x,selectRect.end_y),(128,128,128), 1)
            cv2.rectangle(result_image,(followRect.start_x,followRect.start_y),(followRect.end_x,followRect.end_y),(255,255,255), 1)
    
            # Menampilkan jarak
            distance = Distance(depth_buf)
            print(f'Left:{round(distance.left(),2)} | Center:{round(distance.center(),2)} | Right:{round(distance.right(),2)}')
            distance.rules()
            
            # Memulai Rekaman
            out_raw.write(amplitude_buf)
            out_depth.write(result_image)
            # Menampilkan frame camera
            cv2.imshow("preview_amplitude", amplitude_buf.astype(np.uint8))
            cv2.imshow("preview",result_image)

            key = cv2.waitKey(1)
            if key == ord("q"):
                exit_ = True
                cam.stop()
                cam.close()
                out_raw.release()  
                out_depth.release()
                cv2.destroyAllWindows()
                sys.exit(0)
