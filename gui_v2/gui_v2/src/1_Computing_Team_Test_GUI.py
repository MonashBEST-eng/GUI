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





#######################################
#### FUNCTION FILE INSTANTIATIONS #####
#######################################

## import commands module
import GTW_Control_Comms.gtw_mqtt_commands as gtw_mqtt_commands
gtw_mqtt_commands.start_mqtt()

# import control pannel - digital button box in GUI - this links the GUI control panel menu option to its actual menu 
from GUI_menus.control_panel import open_control_panel
from GUI_menus.button_box_link_panel import open_button_panel, get_button_box
from GUI_menus.monitoring_panel import open_monitoring_panel, update_sensor
from GUI_menus.demo_mode import open_demo_window
from GUI_menus.sbg_panel import open_sbg_panel, update_sbg
from IO_devices.sbg_reader import SbgReader

# import button box module - physical button box
# incorporated into gui to allow setting of com port, and ensuring it is active :)
button_box = get_button_box()   # shared instance — uses the same msg_queue as MQTT
sbg_reader = SbgReader(gtw_mqtt_commands.msg_queue)  # SBG USB reader — connect via SBG IMU panel


# =========================
# MQTT COMMAND DECODER
# =========================
def _decode_mqtt_command(mqtt_msg):
    """
    Convert raw MQTT topic/payload to human-readable command.
    mqtt_msg format: "topic | payload"
    Returns: Human-readable string or None
    """
    try:
        if " | " not in mqtt_msg:
            return None
        topic, payload = mqtt_msg.split(" | ", 1)
        
        # Emergency commands (check payload first for specificity)
        if "EMERGENCY" in payload.upper():
            if "CLEAR" in payload.upper():
                return "🟢 Clear Emergency"
            elif "STOP" in payload.upper():
                return "🚨 EMERGENCY STOP"
            else:
                return "🚨 Emergency Command"
        
        # Safe Mode (check before emergency topic check)
        if "SAFE_MODE" in payload.upper() or "SAFE MODE" in payload.upper():
            return "🟡 Safe Mode"
        
        # Emergency in topic only (fallback)
        if "EMERGENCY" in topic.upper():
            return "🚨 Emergency Command"
        
        # Operation modes
        if "operation_mode" in topic:
            if "AUTO" in payload:
                return "Mode → AUTO"
            elif "MANUAL" in payload:
                return "Mode → MANUAL"
            elif "MAINTENANCE" in payload:
                return "Mode → MAINTENANCE"
        
        # Cutterhead commands
        if "cutterhead" in topic:
            if "speed_increase" in payload or "INCREASE" in payload:
                return "Cutterhead → Speed Increase"
            elif "speed_decrease" in payload or "DECREASE" in payload:
                return "Cutterhead → Speed Decrease"
            elif "slow_spin" in payload:
                return "Cutterhead → Slow Spin"
            elif "fast_spin" in payload:
                return "Cutterhead → Fast Spin"
            elif "STOP" in payload:
                return "Cutterhead → STOP"
            elif "ON" in payload or "START" in payload:
                return "Cutterhead → START"
        
        # Mobility commands
        if "mobility" in topic:
            if "FORWARD" in payload:
                return "Advance → FORWARD"
            elif "REVERSE" in payload or "BACKWARD" in payload:
                return "Advance → REVERSE"
            elif "STOP" in payload:
                return "Advance → STOP"
        
        # Conveyor commands
        if "conveyor" in topic or "conveyer" in topic:
            if "ON" in payload or "START" in payload:
                return "Conveyor → ON"
            elif "OFF" in payload or "STOP" in payload:
                return "Conveyor → OFF"
        
        # Startup procedure
        if "startup" in topic:
            if "READY" in payload:
                return "System → READY"
            elif "START" in payload:
                return "System → START SEQUENCE"
        
        # LED commands
        if "led" in topic:
            return f"LED → {payload}"
        
        # Default: show topic endpoint + payload
        topic_parts = topic.split("/")
        endpoint = topic_parts[-1] if topic_parts else topic
        return f"{endpoint.replace('_', ' ').title()} → {payload}"
    
    except Exception:
        return None




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
root.geometry("1920x1080")
root.configure(bg=BG_MAIN)


# =========================
# HEADER
# =========================
header = tk.Frame(root, bg=BG_PANEL, height=70)
header.pack(fill="x")

# --- TITLE (no logo in header) ---
tk.Label(header, text="TBM CONTROL SYSTEM",
         fg="white", bg=BG_PANEL,
         font=("Segoe UI", 20, "bold")).pack(side="left", padx=20)

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
sidebar = tk.Frame(main, bg=BG_PANEL, width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

def nav_button(text):
    return tk.Button(sidebar, text=text,
                     bg=BG_PANEL, fg="white",
                     relief="flat", anchor="w",
                     padx=20, pady=12)

nav_button("Dashboard").pack(fill="x")

# MONITORING MENU OPEN BUTTON
monitoring_btn = nav_button("Monitoring")
monitoring_btn.pack(fill="x")
monitoring_btn.config(command=lambda: open_monitoring_panel(root))

nav_button("Alarms").pack(fill="x")
nav_button("System Log").pack(fill="x")
nav_button("Settings").pack(fill="x")

# CONTROL PANEL MENU OPEN BUTTON
ctrl_btn = nav_button("Control Panel")
ctrl_btn.pack(fill="x")
ctrl_btn.config(command=lambda: open_control_panel(root))

# BUTTON BOX MENU OPEN BUTTON
btn_box_btn = nav_button("Button Box")
btn_box_btn.pack(fill="x")
btn_box_btn.config(command=lambda: open_button_panel(root))

# SBG IMU MENU OPEN BUTTON
sbg_btn = nav_button("SBG IMU")
sbg_btn.pack(fill="x")
sbg_btn.config(command=lambda: open_sbg_panel(root))

# DEMO MODE BUTTON — visually distinct at bottom of sidebar
tk.Frame(sidebar, bg="#1e3a1e", height=1).pack(fill="x", pady=8)
demo_btn = tk.Button(sidebar, text="🎬  Demo Mode",
                     bg="#14532d", fg="#4ade80",
                     relief="flat", anchor="w",
                     padx=20, pady=12,
                     font=("Segoe UI", 9, "bold"),
                     command=lambda: open_demo_window(root))
demo_btn.pack(fill="x")

# =========================
# SIDEBAR STATUS INDICATORS
# =========================
tk.Frame(sidebar, bg="#1e2a3a", height=1).pack(fill="x", pady=8)

def _indicator(text):
    row = tk.Frame(sidebar, bg=BG_PANEL)
    row.pack(fill="x", padx=14, pady=3)
    dot = tk.Label(row, text="●", fg="#ef4444", bg=BG_PANEL,
                   font=("Segoe UI", 9))
    dot.pack(side="left")
    tk.Label(row, text=f"  {text}", fg="#6b7280", bg=BG_PANEL,
             font=("Segoe UI", 8)).pack(side="left")
    return dot

ind_mqtt   = _indicator("MQTT")
ind_btnbox = _indicator("Button Box")
ind_tbm    = _indicator("TBM Ready")

# =========================
# SIDEBAR SUMMARY CARDS
# (moved from top of content area)
# =========================
tk.Frame(sidebar, bg="#1e2a3a", height=1).pack(fill="x", pady=8)

def create_card(parent, title, value, color):
    card = tk.Frame(parent, bg=BG_CARD)
    card.pack(fill="x", padx=10, pady=4)
    tk.Label(card, text=title, fg="gray", bg=BG_CARD,
             font=("Segoe UI", 7)).pack(anchor="w", padx=8, pady=(5, 0))
    val = tk.Label(card, text=value, fg=color, bg=BG_CARD,
                   font=("Segoe UI", 13, "bold"))
    val.pack(anchor="w", padx=8, pady=(0, 5))
    return val

status_val = create_card(sidebar, "STATUS", "DISCONNECTED", "#ef4444")

# Removed cards — stub labels kept so update_ui doesn't crash
class _Stub:
    def config(self, **_): pass
temp_val  = _Stub()
press_val = _Stub()
flow_val  = _Stub()

def _update_status(connected: bool):
    if connected:
        status_val.config(text="NORMAL", fg="lime")
    else:
        status_val.config(text="DISCONNECTED", fg="#ef4444")

# =========================
# LOGO AT BOTTOM OF SIDEBAR
# =========================
# Spacer to push logo to bottom
tk.Frame(sidebar, bg=BG_PANEL).pack(fill="both", expand=True)

# Logo
img_path = resource_path("GUI_images/logo.png")
logo_img = Image.open(img_path).resize((100, 100))
logo = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(sidebar, image=logo, bg=BG_PANEL)
logo_label.image = logo  # Keep reference
logo_label.pack(side="bottom", pady=15)

# =========================
# CONTENT AREA — scrollable canvas so nothing gets cut on resize
# =========================
content_outer = tk.Frame(main, bg=BG_MAIN)
content_outer.pack(side="left", fill="both", expand=True)

content_canvas = tk.Canvas(content_outer, bg=BG_MAIN, highlightthickness=0)
content_scroll = tk.Scrollbar(content_outer, orient="vertical",
                               command=content_canvas.yview)
content_canvas.configure(yscrollcommand=content_scroll.set)

content_canvas.pack(side="left", fill="both", expand=True)
content_scroll.pack(side="right", fill="y")

content = tk.Frame(content_canvas, bg=BG_MAIN)

def _on_content_configure(e):
    content_canvas.configure(scrollregion=content_canvas.bbox("all"))

def _on_canvas_width(e):
    content_canvas.itemconfig(_content_window, width=e.width)

content.bind("<Configure>", _on_content_configure)
content_canvas.bind("<Configure>", _on_canvas_width)

_content_window = content_canvas.create_window((0, 0), window=content, anchor="nw")

# Mousewheel scroll
def _on_mousewheel(event):
    content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# =========================
# LIVE SENSOR GRID
# =========================
sensor_grid_outer = tk.Frame(content, bg=BG_CARD)
sensor_grid_outer.pack(fill="x", padx=15, pady=(12, 0))

sensor_grid_hdr = tk.Frame(sensor_grid_outer, bg=BG_CARD)
sensor_grid_hdr.pack(fill="x", padx=12, pady=(8, 4))

tk.Label(sensor_grid_hdr, text="LIVE SENSOR READINGS",
         fg="cyan", bg=BG_CARD,
         font=("Segoe UI", 10, "bold")).pack(side="left")

sensor_grid = tk.Frame(sensor_grid_outer, bg=BG_CARD)
sensor_grid.pack(fill="x", padx=8, pady=(0, 8))

SENSOR_COLS = 5

# Sensor tile spec: key → (label, unit, color, warn, crit)
SENSOR_TILE_DEFS = {
    "TEMP_CUTTERHEAD":   ("Cutterhead Temp",    "°C",     "orange",   60,  80),
    "TEMP_MOTOR":        ("Motor Temp",          "°C",     "orange",   70,  90),
    "TEMP_HYDRAULIC":    ("Hydraulic Temp",      "°C",     "orange",   55,  75),
    "TEMP_AMBIENT":      ("Ambient Temp",        "°C",     "orange",   40,  50),
    "PRESS_HYDRAULIC":   ("Hydraulic Press",     "bar",    "cyan",    180, 220),
    "PRESS_CUTTERHEAD":  ("Cutterhead Press",    "bar",    "cyan",    150, 200),
    "PRESS_GREASE":      ("Grease Pressure",     "bar",    "cyan",     80, 120),
    "PRESS_AIR":         ("Air Pressure",        "bar",    "cyan",      8,  10),
    "VOLT_MAIN":         ("Main Bus Voltage",    "V",      "#facc15", 260, 270),
    "VOLT_CONTROL":      ("Control Voltage",     "V",      "#facc15",  26,  28),
    "CURR_CUTTERHEAD":   ("Cutterhead Current",  "A",      "#fb923c",  80, 100),
    "CURR_CONVEYOR":     ("Conveyor Current",    "A",      "#fb923c",  40,  55),
    "CURR_MOTOR":        ("Motor Current",       "A",      "#fb923c",  90, 120),
    "RPM_CUTTERHEAD":    ("Cutterhead RPM",      "rpm",    "#a78bfa",   8,  12),
    "TORQUE_CUTTERHEAD": ("Cutterhead Torque",   "kNm",    "#a78bfa",  80, 100),
    "SPEED_ADVANCE":     ("Advance Speed",       "mm/min", "#a78bfa",  80, 100),
    "FORCE_THRUST":      ("Thrust Force",        "kN",     "#a78bfa",2000,2500),
    "FLOW_HYDRAULIC":    ("Hydraulic Flow",      "L/min",  "#34d399",  90, 110),
    "FLOW_COOLANT":      ("Coolant Flow",        "L/min",  "#34d399",  40,  55),
    "BATTERY_SOC":       ("Battery SOC",         "%",      ACCENT,     20,  10),
}

# Holds label refs so update_sensor_tile() can update them from update_ui()
_tile_labels = {}

for i, (key, spec) in enumerate(SENSOR_TILE_DEFS.items()):
    s_label, unit, color, warn, crit = spec
    row, col = divmod(i, SENSOR_COLS)
    sensor_grid.columnconfigure(col, weight=1)

    tile = tk.Frame(sensor_grid, bg=BG_MAIN, padx=6, pady=6)
    tile.grid(row=row, column=col, padx=4, pady=4, sticky="ew")

    tk.Label(tile, text=s_label, fg="#6b7280", bg=BG_MAIN,
             font=("Segoe UI", 7)).pack(anchor="w")

    val_lbl = tk.Label(tile, text=f"-- {unit}", fg=color, bg=BG_MAIN,
                       font=("Segoe UI", 13, "bold"))
    val_lbl.pack(anchor="w")

    bar = tk.Frame(tile, bg=ACCENT, height=3)
    bar.pack(fill="x", pady=(3, 0))

    _tile_labels[key] = (val_lbl, color, warn, crit, unit)

def update_sensor_tile(key, value):
    """Update a sensor tile from update_ui(). Mirrors update_sensor() for monitoring panel."""
    if key not in _tile_labels:
        return
    val_lbl, base_color, warn, crit, unit = _tile_labels[key]
    try:
        fval = float(value)
        text = f"{fval:.2f} {unit}"
        # SOC inverted (low = bad)
        if warn > crit:
            color = "#ef4444" if fval <= crit else "#f97316" if fval <= warn else base_color
        else:
            color = "#ef4444" if fval >= crit else "#f97316" if fval >= warn else base_color
    except (ValueError, TypeError):
        text = f"{value} {unit}"
        color = base_color
    val_lbl.config(text=text, fg=color)

# =========================
# CAMERA FEEDS
# =========================
cam_row = tk.Frame(content, bg=BG_MAIN)
cam_row.pack(fill="both", expand=True, padx=15, pady=(10, 6))
cam_row.columnconfigure(0, weight=1)
cam_row.columnconfigure(1, weight=1)

def make_camera_panel(parent, col, label):
    """Build a camera feed tile with a disconnected placeholder."""
    frame = tk.Frame(parent, bg=BG_CARD)
    frame.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 6 if col == 0 else 0))
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)

    # Header row
    hdr = tk.Frame(frame, bg=BG_CARD)
    hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))

    tk.Label(hdr, text=f"📷  {label}",
             fg="white", bg=BG_CARD,
             font=("Segoe UI", 11, "bold")).pack(side="left")

    cam_dot = tk.Label(hdr, text="●", fg="#ef4444", bg=BG_CARD,
                       font=("Segoe UI", 12))
    cam_dot.pack(side="right", padx=(0, 4))

    tk.Label(hdr, text="No Signal",
             fg="gray", bg=BG_CARD,
             font=("Segoe UI", 9)).pack(side="right", padx=(0, 6))

    # Feed canvas — draws disconnected placeholder
    feed = tk.Canvas(frame, bg="#0a0a0a", highlightthickness=0)
    feed.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)

    def _draw_placeholder(event=None):
        feed.delete("placeholder")
        w = feed.winfo_width()
        h = feed.winfo_height()
        if w < 2 or h < 2:
            return

        # Dark grid lines to look like a camera viewfinder
        for i in range(0, w, 40):
            feed.create_line(i, 0, i, h, fill="#1a1a2e", tags="placeholder")
        for j in range(0, h, 40):
            feed.create_line(0, j, w, j, fill="#1a1a2e", tags="placeholder")

        # Centre crosshair
        cx, cy = w // 2, h // 2
        feed.create_line(cx - 20, cy, cx + 20, cy, fill="#374151", width=2, tags="placeholder")
        feed.create_line(cx, cy - 20, cx, cy + 20, fill="#374151", width=2, tags="placeholder")

        # Camera icon (simple rectangle + lens circle)
        bw, bh = 80, 54
        bx, by = cx - bw // 2, cy - bh // 2 - 10
        feed.create_rectangle(bx, by, bx + bw, by + bh,
                               outline="#374151", width=2, tags="placeholder")
        feed.create_oval(cx - 16, cy - 26, cx + 16, cy + 2,
                         outline="#374151", width=2, tags="placeholder")
        # viewfinder bump
        feed.create_rectangle(bx + bw - 18, by - 8, bx + bw - 6, by,
                               outline="#374151", width=2, tags="placeholder")

        # Status text
        feed.create_text(cx, cy + 34,
                         text="CAMERA DISCONNECTED",
                         fill="#4b5563", font=("Segoe UI", 10, "bold"),
                         tags="placeholder")
        feed.create_text(cx, cy + 52,
                         text="Waiting for video source...",
                         fill="#374151", font=("Segoe UI", 8),
                         tags="placeholder")

    feed.bind("<Configure>", _draw_placeholder)

    return feed, cam_dot

cam1_feed, cam1_dot = make_camera_panel(cam_row, 0, "CAMERA 1  —  Forward View")
cam2_feed, cam2_dot = make_camera_panel(cam_row, 1, "CAMERA 2  —  Cutterhead View")

# keep alarm_box alive so add_alarm() doesn't crash (hidden, no longer visible)
alarm_box = tk.Text()   # off-screen dummy

# =========================
# LOG PANELS — side by side
# =========================
logs_row = tk.Frame(content, bg=BG_MAIN)
logs_row.pack(fill="both", expand=True, padx=15, pady=(0, 15))
logs_row.columnconfigure(0, weight=1)
logs_row.columnconfigure(1, weight=1)

# ---- LEFT: Ethernet / MQTT Comms Log ----
comms_frame = tk.Frame(logs_row, bg=BG_CARD)
comms_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

comms_hdr = tk.Frame(comms_frame, bg=BG_CARD)
comms_hdr.pack(fill="x", padx=10, pady=(8, 0))

tk.Label(comms_hdr, text="⬡  ETHERNET COMMS LOG",
         fg="#38bdf8", bg=BG_CARD,
         font=("Segoe UI", 11, "bold")).pack(side="left")

# MQTT connection status dot
mqtt_dot = tk.Label(comms_hdr, text="●", fg="#ef4444", bg=BG_CARD,
                    font=("Segoe UI", 12))
mqtt_dot.pack(side="right", padx=(0, 4))
mqtt_status_lbl = tk.Label(comms_hdr, text="Disconnected",
                            fg="gray", bg=BG_CARD,
                            font=("Segoe UI", 9))
mqtt_status_lbl.pack(side="right", padx=(0, 6))

comms_box = tk.Text(comms_frame, bg=BG_MAIN, fg="#38bdf8",
                    font=("Consolas", 9), wrap="none")
comms_box.pack(fill="both", expand=True, padx=10, pady=8)

# colour tags for RX / TX
comms_box.tag_config("rx",     foreground="#38bdf8")   # blue  — incoming
comms_box.tag_config("tx",     foreground="#a3e635")   # green — outgoing
comms_box.tag_config("conn",   foreground="#fb923c")   # orange — connection events
comms_box.tag_config("err",    foreground="#ef4444")   # red   — errors

# ---- RIGHT: Control Log ----
status_frame = tk.Frame(logs_row, bg=BG_CARD)
status_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

tk.Label(status_frame, text="🎮  CONTROL LOG",
         fg="#a78bfa", bg=BG_CARD,
         font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 0))

status_box = tk.Text(status_frame, bg=BG_MAIN, fg="#e5e7eb",
                     font=("Consolas", 9), wrap="none")
status_box.pack(fill="both", expand=True, padx=10, pady=8)

# colour tags
status_box.tag_config("btn",   foreground="#c084fc")   # purple — button box
status_box.tag_config("alarm", foreground="#ef4444")   # red    — alarms
status_box.tag_config("info",  foreground="#e5e7eb")   # white  — general
status_box.tag_config("warn",  foreground="#fb923c")   # orange — warnings

# =========================
# LOGGING FUNCTIONS
# =========================
MAX_LOG_LINES = 500   # cap both logs to avoid memory creep

def _append(box, msg, tag):
    box.insert(tk.END, msg + "\n", tag)
    box.see(tk.END)
    # trim oldest lines when cap is hit
    lines = int(box.index("end-1c").split(".")[0])
    if lines > MAX_LOG_LINES:
        box.delete("1.0", f"{lines - MAX_LOG_LINES}.0")

def log_comms(msg, tag="rx"):
    """Write to the Ethernet Comms log. tag: 'rx' | 'tx' | 'conn' | 'err'"""
    t = time.strftime("%H:%M:%S")
    _append(comms_box, f"[{t}] {msg}", tag)

def log_status(msg, tag="info"):
    """Write to the System Status log. tag: 'info' | 'btn' | 'alarm' | 'warn'"""
    t = time.strftime("%H:%M:%S")
    _append(status_box, f"[{t}] {msg}", tag)

# Keep a single log() alias for any legacy calls — routes to status log
def log(msg, color="white"):
    log_status(msg, tag="info")

def add_alarm(msg):
    alarm_box.insert(tk.END, msg + "\n")
    log_status(f"ALARM: {msg}", tag="alarm")



# =========================
# GRAPH — update_graph kept as a no-op so sensor routing still compiles
# (graph panel removed — replaced by camera feeds)
# =========================
def update_graph(v):
    pass

# =========================
# SERIAL / MESSAGE HANDLER
# =========================
def update_ui():
    while not gtw_mqtt_commands.msg_queue.empty():
        msg_type, data = gtw_mqtt_commands.msg_queue.get()

        # ---- MQTT connection events → comms log + MQTT indicator only ----
        if msg_type == "conn":
            connected = "Connected" in data
            mqtt_dot.config(fg="#22c55e" if connected else "#ef4444")
            mqtt_status_lbl.config(text=data)
            ind_mqtt.config(fg="#22c55e" if connected else "#ef4444")
            _update_status(connected)
            log_comms(f"[MQTT] {data}", tag="conn")
            # not logged to control log — MQTT only goes to comms log

        # ---- Incoming MQTT data → comms log + all sensor displays ----
        elif msg_type == "mqtt_rx":
            log_comms(f"[RX] {data}", tag="rx")

            # Each received packet counts as TBM alive — green TBM Ready dot
            ind_tbm.config(fg="#22c55e")

            # Parse telemetry — format:  topic | KEY:val,KEY:val,...
            try:
                payload = data.split("|")[1].strip()

                for p in payload.split(","):
                    key, val = p.split(":")
                    val = float(val)

                    # ---- Dashboard summary cards ----
                    if key == "TEMP":
                        temp_val.config(text=f"{val} °C")
                        update_graph(val)
                        update_sensor("TEMP_CUTTERHEAD", val)
                        update_sensor_tile("TEMP_CUTTERHEAD", val)

                    elif key == "PRESS":
                        press_val.config(text=f"{val} bar")
                        update_sensor("PRESS_HYDRAULIC", val)
                        update_sensor_tile("PRESS_HYDRAULIC", val)

                    elif key == "FLOW":
                        flow_val.config(text=f"{val} L/min")
                        update_sensor("FLOW_HYDRAULIC", val)
                        update_sensor_tile("FLOW_HYDRAULIC", val)

                    # ---- All other sensors — monitoring panel + main tile ----
                    else:
                        update_sensor(key, val)
                        update_sensor_tile(key, val)

            except:
                pass

        # ---- Outgoing MQTT commands → comms log + control log ----
        elif msg_type == "mqtt_tx":
            log_comms(f"[TX] {data}", tag="tx")
            # Also log human-readable command to Control Log
            readable_cmd = _decode_mqtt_command(data)
            if readable_cmd:
                log_status(f"[CMD] {readable_cmd}", tag="btn")

        # ---- SBG IMU data → sbg panel ----
        elif msg_type == "sbg_rx":
            # data is expected to be a dict: {"roll": x, "pitch": y, ...}
            update_sbg(data)
            # Don't spam comms log with continuous SBG data

        # ---- SBG connection status → comms log ----
        elif msg_type == "sbg_status":
            log_comms(f"{data}", tag="conn")

        # ---- Physical button box events → status log + button box indicator ----
        elif msg_type == "btn_status":
            connected = "Connected" in data
            ind_btnbox.config(fg="#22c55e" if connected else "#ef4444")
            log_status(f"[BTN BOX] {data}", tag="btn")

        elif msg_type == "btn_press":
            log_status(f"[BTN BOX] Button {data} pressed", tag="btn")

        elif msg_type == "btn_toggle":
            btn_id, state = data
            log_status(f"[BTN BOX] Toggle {btn_id} → {'ON' if state else 'OFF'}", tag="btn")

        # ---- Fallback → status log ----
        else:
            log_status(str(data), tag="info")

    root.after(100, update_ui)

update_ui()

# =========================
# RUN
# =========================
root.mainloop()