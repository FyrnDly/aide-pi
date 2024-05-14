import numpy as np
import random
import ArducamDepthCamera as ac
import serial
import pickle
import os.path as path

class PolicyGradientAgent:
    def __init__(self, alpha=0.1, epsilon=0.01, road_condition=0):
        self.alpha = alpha
        self.epsilon = epsilon
        self.parameters = np.array([80, 60])  # Parameter untuk aturan
        self.road_condition = road_condition  # 0 untuk kering, 1 untuk licin

    def choose_action(self, state):
        left, front, right = state
        if self.road_condition == 1:  # Jika jalan licin, gunakan ambang batas yang lebih tinggi
            threshold = self.parameters[0] + 20
        else:
            threshold = self.parameters[0]
        if front > threshold:  # Parameter 0 adalah ambang batas untuk jarak tengah
            action = 1
        elif self.parameters[1] < front <= threshold:  # Parameter 1 adalah ambang batas lain untuk jarak tengah
            if right > left:
                action = 2    # kanan
            else:
                action = 3    # kiri
        elif front <= self.parameters[1]:
            action = 4
        else:
            action = 0   # Mobil berhenti untuk menilai lingkungan
        return action

    def update_parameters(self, state, action):
        # Hitung gradien dari expected reward terhadap parameter
        grad = np.zeros_like(self.parameters)
        for i in range(len(self.parameters)):
            old_param = self.parameters[i]
            self.parameters[i] = old_param + self.epsilon
            reward_plus = self.get_expected_reward(state, action)
            self.parameters[i] = old_param - self.epsilon
            reward_minus = self.get_expected_reward(state, action)
            self.parameters[i] = old_param  # Kembalikan parameter ke nilai aslinya
            grad[i] = (reward_plus - reward_minus) / (2 * self.epsilon)

        # Perbarui parameter menggunakan gradien
        self.parameters += self.alpha * grad


    def get_expected_reward(self, state, action):
        # Implementasikan fungsi ini untuk menghitung expected reward
        left, front, right = state
        if action == 1:
            reward = 0
        elif front < 60 or action == 0 or action == 4:
            reward = -1
        else:
            reward = 1
        return reward
    
    def get_com(self, action):
        # Mengirim sinyal ke Arduino berdasarkan action
        if action == 0:
            ser.write(b'berhenti')
        elif action == 1:
            ser.write(b'maju')
        elif action == 2:
            ser.write(b'kanan')
        elif action == 3: 
            ser.write(b'kiri')
        elif action == 4:
            ser.write(b'mundur')

def get_current_state(depth_buf):
    # Mengambil jarak di posisi tengah, kiri, dan kanan frame
    y = depth_buf.shape[0] // 2
    x_center = depth_buf.shape[1] // 2
    x_left = depth_buf.shape[1] // 4
    x_right = depth_buf.shape[1] * 3 // 4

    center_distance = depth_buf[y, x_center] * 100  # Mengubah jarak ke cm
    left_distance = depth_buf[y, x_left] * 100  # Mengubah jarak ke cm
    right_distance = depth_buf[y, x_right] * 100  # Mengubah jarak ke cm

    state = (left_distance, center_distance, right_distance)
    return state

# Initialize RL agent
if path.isfile('model.pkl'):
    with open('model.pkl','rb') as model:
        agent = model
else:
    agent = PolicyGradientAgent()

try:
    # Cek Kondisi jalanan
    road_condition = 0 # Update dengan API
    agent.road_condition = road_condition
    # Membuat objek serial untuk komunikasi dengan Arduino
    ser = serial.Serial('/dev/ttyACM0', 9600)
    cam = ac.ArducamCamera()
    # Initialize camera
    if cam.open(ac.TOFConnect.CSI,0) != 0 :
        print("initialization failed")
    if cam.start(ac.TOFOutput.DEPTH) != 0 :
        print("Failed to start camera")
    # Main loop
    while True:
        # Get current state
        frame = cam.requestFrame(200)
        if frame != None:
            depth_buf = frame.getDepthData()
            cam.releaseFrame(frame)
            state = get_current_state(depth_buf)
            # Choose action
            action = agent.choose_action(state)
            # Com serial
            agent.get_com(action)
            # Update Parameters
            agent.update_parameters(state, action)

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Errors {e}")
finally:
    with open('model.pkl','wb') as model:
        pickle.dump(agent,model)