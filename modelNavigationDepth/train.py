import time
import ArducamDepthCamera as ac
import serial
import logging
import time

class AgentModel:
    def __init__(self, alpha=0.1, epsilon=0.1, road_condition=0, parameter=70, threshold=50, length_agent=85, parameter_road_condition=20):
        self.alpha = alpha
        self.epsilon = epsilon
        self.parameter = parameter  # Parameter untuk aturan jarak depan sensor
        self.threshold = threshold
        self.road_condition = road_condition  # 0 untuk kering, 1 untuk licin
        self.length_agent = length_agent
        self.parameter_road_condition = parameter_road_condition

    def choose_action(self, state):
        left, front, right = state
        if self.road_condition == 1:  # Jika jalan licin, gunakan ambang batas yang lebih tinggi
            self.parameter = self.parameter + self.parameter_road_condition
        else:
            self.parameter = self.parameter
        if front > self.parameter:  # Parameter 0 adalah ambang batas untuk jarak tengah
            action = 1
        elif self.threshold < front <= self.parameter:  # Parameter 1 adalah ambang batas lain untuk jarak tengah
            if right > left:
                action = 2    # kanan
            else:
                action = 3    # kiri
        elif front <= self.threshold:
            action = 4      # mundur
        else:
            action = 0   # Mobil berhenti untuk menilai lingkungan
        return action

    def update_parameters(self, state, action):
        # Hitung gradien dari expected reward terhadap parameter
        grad = 0
        old_parameter = self.parameter
        self.parameter += self.epsilon * self.parameter
        reward_plus = self.get_expected_reward(state, action)
        self.parameter = old_parameter
        self.parameter -= self.epsilon * self.parameter
        reward_minus = self.get_expected_reward(state, action)
        grad = (reward_plus + reward_minus) / (2 * self.epsilon)
        self.parameter = old_parameter

        # Perbarui parameter menggunakan gradien
        self.parameter += self.alpha * grad


    def get_expected_reward(self, state, action):
        # Implementasikan fungsi ini untuk menghitung expected reward
        left, front, right = state
        if action == 0 or action == 4 or front < self.threshold:
            reward = 1
        elif action == 2:
            if left > self.length_agent or right < self.length_agent:
                reward = -1.5
            else:
                reward = 0
        elif action == 3:
            if right > self.length_agent or left < self.length_agent:
                reward = -1.5
            else:
                reward = 0
        else:
            reward = 0
        return reward
    
    def get_com(self, action):
        # Mengirim sinyal ke Arduino berdasarkan action
        if action == 0:
            ser.write(b'berhenti\n')
            # pass
        elif action == 1:
            ser.write(b'maju\n')
            # pass
        elif action == 2:
            ser.write(b'kanan\n')
            # pass
        elif action == 3: 
            ser.write(b'kiri\n')
            # pass
        elif action == 4:
            ser.write(b'mundur\n')
            # pass

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
agent = AgentModel()

# Add Log Info
logging.basicConfig(filename='output.log', level=logging.INFO)
logging.info("Mulai Program")
print("Mulai Program")
# Cek Kondisi jalanan
road_condition = 0 # Update dengan API
agent.road_condition = road_condition
# Membuat objek serial untuk komunikasi dengan Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)
cam = ac.ArducamCamera()
# Initialize camera
if cam.open(ac.TOFConnect.CSI,0) != 0 :
    logging.info("initialization failed")
    print("initialization failed")
if cam.start(ac.TOFOutput.DEPTH) != 0 :
    logging.info("Failed to start camera")
    print("Failed to start camera")
# Main loop
start_time = time.monotonic()
while True:
    try:
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
            
        # Log Output Status
        if action == 0:
            status = 'berhenti'
        elif action == 1:
            status = 'maju'
        elif action == 2:
            status = 'kanan'
        elif action == 3: 
            status = 'kiri'
        elif action == 4:
            status = 'mundur'
        print(f"Status: {status} | Parameters: {agent.parameter}\nDistance: {state}")
        # Check Status on Arduino
        response = ser.readline().decode().strip()
        if response:
            try:
                print(f"Status pada Arduino: {response}")
            except Exception as e:
                print(f"Gagal terhubung: {str(e)} | {type(response)}")
        # Print Status every second
        # Check current time
        current_time = time.monotonic()
        elapsed_time = current_time - start_time
        if elapsed_time >= 1:
            # Mengirim sinyal ke Arduino berdasarkan action
            logging.info(f"Status: {status} | Parameters: {agent.parameter}\nDistance: {state}")
            start_time = current_time
    except KeyboardInterrupt:
        break