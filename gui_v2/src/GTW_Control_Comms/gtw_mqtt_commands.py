## THIS FUNCTION FILE CONTAINS THE MQTT ETHERNET BRAINWORK TO SEND COMMANDS TO THE GATEWAY ECU

# import required modules
import paho.mqtt.client as mqtt
import threading
import time
from queue import Queue

# ==================================================
# # ---------------- MQTT CONFIG ----------------
# ==================================================
# STM BROKER ADDRESS
BROKER = "192.168.1.10"#"192.168.1.10"
PORT = 1883

# USE THIS IF NOT USING STM H7
# BROKER = "localhost"
# PORT = 1883

msg_queue = Queue()
client = mqtt.Client()

# ==================================================
# DEFINE_MQTT_topics
# ordrerd based on control panel button order
# ==================================================
TOPIC_EMERGENCY = "tbm/EMERGENCY_STOP"
TOPIC_SYS_INIT_START = "tbm/startup_procedure"
TOPIC_OPERATION_MODE = "tbm/operation_mode"
TOPIC_MOBILITY = "tbm/mobility"
TOPIC_CUTTERHEAD = "tbm/cutterhead"
TOPIC_CONVEYER = "tbm/conveyer"

# H7 TESTING TOPIC :)
TOPIC_LED = "stm32/led"

# Required for subscribing - confirming connection :)
TOPIC_SUB = "stm32/#"


# other random topics/ideas not used
# TOPIC_CMD = "tbm/control"
# TOPIC_TBM_CONTROL = "tbm32/sensor"
# TOPIC_STM32 = "stm32/#"


# NEED TO CLEAN UP THIS AI SLOP MQTT 
# NEED TO CLEAN UP THIS AI SLOP MQTT 
# NEED TO CLEAN UP THIS AI SLOP MQTT 
# NEED TO CLEAN UP THIS AI SLOP MQTT 

# what are userdata, flags even used for in the callback functions :)

# ==================================================
# START MQTT THREAD
# ==================================================
def start_mqtt():
    threading.Thread(target=mqtt_loop, daemon=True).start()

# ==================================================
# CALLBACKS
# ==================================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        msg_queue.put(("conn", "Connected"))
        client.subscribe(TOPIC_SUB)
    else:
        msg_queue.put(("conn", "Connection Failed"))

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    # Push full pipeline
    msg_queue.put(("mqtt_rx", f"{topic} | {payload}"))

client.on_connect = on_connect
client.on_message = on_message

# ==================================================
# MQTT LOOP
# ==================================================
def mqtt_loop():
    while True:
        try:
            client.connect(BROKER, PORT, 60)
            client.loop_forever()
        except Exception as e:
            msg_queue.put(("conn", f"Disconnected: {e}"))
            time.sleep(2)


# AI SLOP ENDED :) AI SLOP ENDED :) AI SLOP ENDED :) AI SLOP ENDED :)


# ===========================================================================
# ===========================================================================
# ===========================================================================
# ===========================================================================
# ===========================================================================

# ===========================================================================
# ================================ COMMANDS =================================
# ===========================================================================
# example command structure - make specific for each intended topic :)
# def send_command(cmd):
#     client.publish(TOPIC_CMD, cmd)
#     msg_queue.put(("mqtt_tx", f"{TOPIC_CMD} | {cmd}"))

# safety control buttons
# status is EMERGENCY_STOP, or SAFE_MODE, or deactivate_emergency
def emergency_mode(status):
    client.publish(TOPIC_EMERGENCY, status)
    msg_queue.put(("mqtt_tx", f"{TOPIC_LED} | {status}"))

# startup initialisation commands - first INITIALISE, then START SYSTEM
# logic implemented on panel side to prevent sending start prior to 15 sec initialisation check period
def system_start_int_mode(state):
    client.publish(TOPIC_SYS_INIT_START, state)
    msg_queue.put(("mqtt_tx", f"{TOPIC_SYS_INIT_START} | {state}"))

# operation mode commands - manual, auto or safe idle
def operation_mode(mode):
    client.publish(TOPIC_OPERATION_MODE, mode)
    msg_queue.put(("mqtt_tx", f"{TOPIC_OPERATION_MODE} | {mode}"))

# mobility commands - most likely for stewart platform control - rn use placeholder eg forward
# def mobility_commands(state, x_axis_val, y_axis_val, z_axis_val):
def mobility_commands(direction):
    client.publish(TOPIC_MOBILITY, direction)
    msg_queue.put(("mqtt_tx", f"{TOPIC_MOBILITY} | {direction}"))

    # once button implemented with ability to enter degrees of stewart platform turn then use this
    # msg_queue.put(("mqtt_tx", f"{TOPIC_SYS_INIT_START} | {x_axis_val} | {y_axis_val} | {z_axis_val}"))

# Cutterhead commands - manual, auto or safe idle
def cutterhead_control(instruction):
    client.publish(TOPIC_CUTTERHEAD, instruction)
    msg_queue.put(("mqtt_tx", f"{TOPIC_CUTTERHEAD} | {instruction}"))

# conveyer control
def conveyer_control(mode):
    client.publish(TOPIC_CONVEYER, mode)
    msg_queue.put(("mqtt_tx", f"{TOPIC_CONVEYER} | {mode}"))


# testing h7 - activate specific led on h7 dev board
def set_led(color):
    client.publish(TOPIC_LED, color)
    msg_queue.put(("mqtt_tx", f"{TOPIC_LED} | {color}"))
