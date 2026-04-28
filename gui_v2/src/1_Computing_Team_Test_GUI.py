import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



## IMPORT REQUIRED GUI PACKAGES
import tkinter as tk
from PIL import Image, ImageTk
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





#######################################
#### FUNCTION FILE INSTANTIATIONS #####
#######################################

## import commands module
import GTW_Control_Comms.gtw_mqtt_commands as gtw_mqtt_commands
gtw_mqtt_commands.start_mqtt()

# import control pannel - digital button box in GUI - this links the GUI control panel menu option to its actual menu 
from GUI_menus.control_panel import open_control_panel

# import button box module - physical button box
# incorporated into gui to allow setting of com port, and ensuring it is active :)





# =========================
# THEME COLORS
# =========================
BG_MAIN = "#0f172a"
BG_PANEL = "#111827"
BG_CARD = "#1f2937"
ACCENT = "#22c55e"
TEXT = "#e5e7eb"

# =========================
# ROOT WINDOW
# =========================
root = tk.Tk()
root.title("Monash BEST TBM Control Interface👷")
root.geometry("1400x800")
root.configure(bg=BG_MAIN)


# =========================
# HEADER
# =========================
header = tk.Frame(root, bg=BG_PANEL, height=70)
header.pack(fill="x")



# logo_img = Image.open("logo.png").resize((177, 177))
img_path = resource_path("GUI_images/logo.png")
logo_img = Image.open(img_path).resize((50, 50))
logo = ImageTk.PhotoImage(logo_img)
tk.Label(header, image=logo, bg=BG_PANEL).pack(side="left", padx=15)

# --- TITLE ---
tk.Label(header, text="TBM CONTROL SYSTEM",
         fg="white", bg=BG_PANEL,
         font=("Segoe UI", 20, "bold")).pack(side="left")

# --- CLOCK ---
time_label = tk.Label(header, fg="white", bg=BG_PANEL, font=("Segoe UI", 12))
time_label.pack(side="right", padx=20)

def update_time():
    now = time.strftime("%H:%M:%S\n%d/%m/%Y")
    time_label.config(text=now)
    root.after(1000, update_time)

update_time()


# =========================
# SAFE SHUTDOWN PROTECTION
# =========================
from tkinter import simpledialog

SHUTDOWN_PASSWORD = "1234"   # change this

def safe_close():
    # Ask confirmation first
    confirm = tk.messagebox.askyesno("Confirm Shutdown",
                                     "Do you want to shut down the SCADA system?")
    if not confirm:
        return

    # Ask password
    pwd = simpledialog.askstring("Authentication",
                                 "Enter shutdown password: 1234",
                                 show="*")

    if pwd == SHUTDOWN_PASSWORD:

        # WHEN SHUTDOWN PASSWORD ENTERED ON ACCIDENTAL EXIT WHILE SYSTEM ACTIVE
        # EXECUTE ALL COMMANDS TO SHUT TBM DOWN SAFELY
        root.destroy()
    else:
        tk.messagebox.showerror("Access Denied", "Incorrect password")

root.protocol("WM_DELETE_WINDOW", safe_close)
root.bind("<Alt-F4>", lambda e: safe_close())





# =========================
# MAIN LAYOUT
# =========================
main = tk.Frame(root, bg=BG_MAIN)
main.pack(fill="both", expand=True)

# =========================
# SIDEBAR
# =========================
sidebar = tk.Frame(main, bg=BG_PANEL, width=200)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

def nav_button(text):
    return tk.Button(sidebar, text=text,
                     bg=BG_PANEL, fg="white",
                     relief="flat", anchor="w",
                     padx=20, pady=12)

nav_button("Dashboard").pack(fill="x")
nav_button("Monitoring").pack(fill="x")
nav_button("Alarms").pack(fill="x")
nav_button("System Log").pack(fill="x")
nav_button("Settings").pack(fill="x")


# CONTROL PANEL MENU OPEN BUTTON
ctrl_btn = nav_button("Control Panel")
ctrl_btn.pack(fill="x")
ctrl_btn.config(command=lambda: open_control_panel(root))

# =========================
# CONTENT AREA
# =========================
content = tk.Frame(main, bg=BG_MAIN)
content.pack(side="left", fill="both", expand=True, padx=15, pady=15)

# =========================
# STATUS CARDS
# =========================
cards_frame = tk.Frame(content, bg=BG_MAIN)
cards_frame.pack(fill="x")

def create_card(parent, title, value, color):
    card = tk.Frame(parent, bg=BG_CARD)
    card.pack(side="left", expand=True, fill="both", padx=10)

    tk.Label(card, text=title, fg="gray",
             bg=BG_CARD).pack(anchor="w", padx=10, pady=5)

    val = tk.Label(card, text=value,
                   fg=color, bg=BG_CARD,
                   font=("Segoe UI", 16, "bold"))
    val.pack(anchor="w", padx=10, pady=5)

    return val

status_val = create_card(cards_frame, "STATUS", "NORMAL", "lime")
temp_val = create_card(cards_frame, "TEMPERATURE", "0 °C", "orange")
press_val = create_card(cards_frame, "PRESSURE", "0 bar", "cyan")
flow_val = create_card(cards_frame, "FLOW RATE", "0 L/min", "violet")

# =========================
# ALARMS PANEL
# =========================
alarm_frame = tk.Frame(content, bg=BG_CARD)
alarm_frame.pack(fill="both", expand=True, pady=10)

tk.Label(alarm_frame, text="ACTIVE ALARMS",
         fg="red", bg=BG_CARD,
         font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10)

alarm_box = tk.Text(alarm_frame, height=6,
                    bg=BG_MAIN, fg="red")
alarm_box.pack(fill="both", padx=10, pady=10)

# =========================
# LOG PANEL
# =========================
log_frame = tk.Frame(content, bg=BG_CARD)
log_frame.pack(fill="both", expand=True)

tk.Label(log_frame, text="SYSTEM LOG",
         fg="cyan", bg=BG_CARD,
         font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10)

log_box = tk.Text(log_frame, bg=BG_MAIN, fg="white")
log_box.pack(fill="both", expand=True, padx=10, pady=10)

# =========================
# LOGGING FUNCTIONS
# =========================
def log(msg, color="white"):
    t = time.strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{t}] {msg}\n")
    log_box.see(tk.END)

def add_alarm(msg):
    alarm_box.insert(tk.END, msg + "\n")



# =========================
# GRAPH (OPTIONAL RIGHT SIDE)
# =========================
graph_frame = tk.Frame(main, bg=BG_PANEL, width=350)
graph_frame.pack(side="right", fill="y")
graph_frame.pack_propagate(False)

fig, ax = plt.subplots(figsize=(4,3))
fig.patch.set_facecolor(BG_PANEL)
ax.set_facecolor(BG_MAIN)
ax.tick_params(colors='white')

data = deque([0]*50, maxlen=50)
line, = ax.plot(data, color="cyan")

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

def update_graph(v):
    data.append(v)
    line.set_ydata(data)
    line.set_xdata(range(len(data)))
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

# =========================
# SERIAL / MESSAGE HANDLER
# =========================
def update_ui():
    while not gtw_mqtt_commands.msg_queue.empty():
        msg_type, data = gtw_mqtt_commands.msg_queue.get()

        if msg_type == "conn":
            log(f"[MQTT STATUS] {data}")

        elif msg_type == "mqtt_rx":
            log(f"[RX] {data}")

            # Parse telemetry
            try:
                payload = data.split("|")[1].strip()

                for p in payload.split(","):
                    key, val = p.split(":")
                    val = float(val)

                    if key == "TEMP":
                        temp_val.config(text=f"{val} °C")
                        update_graph(val)

                    elif key == "PRESS":
                        press_val.config(text=f"{val} bar")

                    elif key == "FLOW":
                        flow_val.config(text=f"{val} L/min")

            except:
            #     log("Parse error")
                pass

        elif msg_type == "mqtt_tx":
            log(f"[TX] {data}")

        else:
            log(data)

    root.after(100, update_ui)

update_ui()

# =========================
# RUN
# =========================
root.mainloop()