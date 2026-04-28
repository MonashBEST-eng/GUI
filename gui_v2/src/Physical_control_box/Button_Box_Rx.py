import serial
import time

# CONTROL BOX LINKING PANEL CONNECTION
# integration into GUI to control COM PORT







## ONCE SETTINGS SET IN GUI THEN START THE BUTTON BOX CONNECTION VIA THE DEFINED COM PORT

# BUTTON BOX LOGIC
# read Arduino button box port
ser = serial.Serial('COM4', 115200, timeout=100000)

# Define states
last_states = [0] * 25
toggle_states = [0] * 25

# DEFINE TOGGLE BUTTONS WHICH ARE COLUMN 1
toggles = set(range(0, 3))


while True:
    line = ser.readline().decode(errors='ignore').strip()
    if not line:
        continue

    parts = line.split()
    if len(parts) != 3:
        continue

    tag, button_id, state = parts

    if tag != "B":
        continue

    button_id = int(button_id)
    state = int(state)

    # --- NORMAL BUTTONS ---
    if button_id not in toggles:
        if state == 1 and last_states[button_id] == 0:
            print(f"Button {button_id} PRESSED")

    # --- TOGGLES ---
    else:
        if state == 1 and last_states[button_id] == 0:
            toggle_states[button_id] ^= 1
            print(f"Toggle {button_id} = {'ON' if toggle_states[button_id] else 'OFF'}")

    last_states[button_id] = state

    # BUTTON DEFINITION LOGIC
    # 1 - 
    


    # 2 - 


    # 23

    # 24


    # 25



    time.sleep(0.001)




