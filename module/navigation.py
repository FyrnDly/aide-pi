import numpy as np

class AgentModel:
    def __init__(self, alpha=0.1, epsilon=0.1, road_condition=0, parameter=80, threshold=60, width_agent=57, parameter_road_condition=20):
        self.alpha = alpha
        self.epsilon = epsilon
        self.parameter = parameter  # Parameter untuk aturan jarak depan sensor
        self.threshold = threshold
        self.road_condition = road_condition  # 0 untuk kering, 1 untuk licin
        self.width_agent = width_agent
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
        grad = np.zeros_like(self.parameter)
        old_parameter = self.parameter
        self.parameter += self.epsilon * self.parameter
        reward_plus = self.get_expected_reward(state, action)
        self.parameter = old_parameter
        self.parameter -= self.epsilon * self.parameter
        reward_minus = self.get_expected_reward(state, action)
        grad = (reward_plus + reward_minus) / (2 * self.epsilon)
        self.parameter = old_parameter

        # Perbarui parameter menggunakan gradien
        self.parameter = self.parameter.astype(float)
        self.parameter += self.alpha * grad


    def get_expected_reward(self, state, action):
        # Implementasikan fungsi ini untuk menghitung expected reward
        left, front, right = state
        if action == 0 or action == 4 or front < self.parameter:
            reward = 1
        elif action == 2 or action == 3:
            if abs(right - left) > (self.width_agent/2):
                reward = -1
        else:
            reward = 0
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