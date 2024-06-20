import time
from module.navigation import get_current_state as state_model

# Program navigation
def navigation_robot(duration, agentModel, camera):
    start_time = time.monotonic()
    while True:
        # Main Program Navigation
        frame = camera.requestFrame(200)
        if frame != None:
            depth_buf = frame.getDepthData()
            camera.releaseFrame(frame)
            state = state_model(depth_buf)
            # Choose action
            action = agentModel.choose_action(state)
            # Com serial
            agentModel.get_com(action)
            # Get Delay Arduino
            ser = agentModel.ser
            response = ser.readline().decode().strip()
            # Update Parameters
            agentModel.update_parameters(state, action)
        
        # Check current time
        current_time = time.monotonic()
        elapsed_time = current_time - start_time
        # Stop program when time out
        if elapsed_time >= duration:
            ser = agentModel.ser
            ser.write(b'berhenti\n')
            break