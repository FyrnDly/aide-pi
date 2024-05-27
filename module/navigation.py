import numpy as np

class PolicyGradientAgent:
    def __init__(self, alpha=0.1, epsilon=1, road_condition=0):
        self.alpha = alpha
        self.epsilon = epsilon
        self.parameters = np.array([80, 60])  # Parameters distance
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
            reward = self.get_expected_reward(state, action)
            grad[i] = reward / self.epsilon

        # Perbarui parameter menggunakan gradien
        self.parameters = self.parameters.astype(float)
        self.parameters += self.alpha * grad


    def get_expected_reward(self, state, action):
        # Implementasikan fungsi ini untuk menghitung expected reward
        left, front, right = state
        if front < self.parameters[1] or action == 0 or action == 4:
            reward = 1
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