# /code/robot_state.py
# possibly obsolete

# Expects global vars to be updated elsewhere in the system (e.g., ibus_input.py or main.py)
# This stub assumes shared memory or injected values (e.g., from ibus decoding)

# You must declare and update these elsewhere:
# - throttle_raw (int, 1000–2000)
# - pivot_raw (int, 1000–2000)
# - brake_active (bool)
# - current_mode (str)

# These should be declared globally in your control logic and updated per frame
throttle_raw = 1500
pivot_raw = 1500
brake_active = False
current_mode = "M1"

def scale_channel(val):
    """Scales IBUS channel from 1000–2000 to -100 to 100"""
    return max(min(round((val - 1500) / 5), 100), -100)

def get_robot_state():
    """Returns a dict of the robot's real-time movement state"""
    return {
        "throttle_pct": scale_channel(throttle_raw),
        "pivot_pct": scale_channel(pivot_raw),
        "brake": brake_active,
        "mode": current_mode
    }
