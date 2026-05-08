# demo_mode.py
# Full duplicate of the main GUI running live simulation.
# Includes: logo, SBG IMU menu with simulated attitude data,
# sensor grid, cameras, comms log, control log.

import tkinter as tk
from tkinter import ttk
import os
import sys
import time
import random
import math

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# =========================
# THEME — identical to main GUI
# =========================
BG_MAIN  = "#0f172a"
BG_PANEL = "#111827"
BG_CARD  = "#1f2937"
ACCENT   = "#22c55e"
TEXT     = "#e5e7eb"

# =========================
# SENSOR DEFINITIONS
# (label, unit, color, warn, crit, base, amplitude, period_s)
# =========================
SENSOR_DEFS = {
    "TEMP_CUTTERHEAD":   ("Cutterhead Temp",    "°C",     "orange",   60,  80,   48,  12, 30),
    "TEMP_MOTOR":        ("Motor Temp",          "°C",     "orange",   70,  90,   62,   8, 25),
    "TEMP_HYDRAULIC":    ("Hydraulic Temp",      "°C",     "orange",   55,  75,   45,   9, 40),
    "TEMP_AMBIENT":      ("Ambient Temp",        "°C",     "orange",   40,  50,   22,   2, 60),
    "PRESS_HYDRAULIC":   ("Hydraulic Press",     "bar",    "cyan",    180, 220,  155,  18, 20),
    "PRESS_CUTTERHEAD":  ("Cutterhead Press",    "bar",    "cyan",    150, 200,  110,  22, 18),
    "PRESS_GREASE":      ("Grease Pressure",     "bar",    "cyan",     80, 120,   58,  14, 35),
    "PRESS_AIR":         ("Air Pressure",        "bar",    "cyan",      8,  10,    7.4, 0.4,50),
    "VOLT_MAIN":         ("Main Bus Voltage",    "V",      "#facc15", 260, 270,  242,   4, 45),
    "VOLT_CONTROL":      ("Control Voltage",     "V",      "#facc15",  26,  28,   24.1, 0.3,55),
    "CURR_CUTTERHEAD":   ("Cutterhead Current",  "A",      "#fb923c",  80, 100,   72,  14, 22),
    "CURR_CONVEYOR":     ("Conveyor Current",    "A",      "#fb923c",  40,  55,   34,   8, 28),
    "CURR_MOTOR":        ("Motor Current",       "A",      "#fb923c",  90, 120,   78,  16, 20),
    "RPM_CUTTERHEAD":    ("Cutterhead RPM",      "rpm",    "#a78bfa",   8,  12,    6.8, 1.2,15),
    "TORQUE_CUTTERHEAD": ("Cutterhead Torque",   "kNm",    "#a78bfa",  80, 100,   62,  14, 18),
    "SPEED_ADVANCE":     ("Advance Speed",       "mm/min", "#a78bfa",  80, 100,   55,  18, 25),
    "FORCE_THRUST":      ("Thrust Force",        "kN",     "#a78bfa",2000,2500, 1650, 300, 20),
    "FLOW_HYDRAULIC":    ("Hydraulic Flow",      "L/min",  "#34d399",  90, 110,   82,  10, 22),
    "FLOW_COOLANT":      ("Coolant Flow",        "L/min",  "#34d399",  40,  55,   44,   6, 30),
    "BATTERY_SOC":       ("Battery SOC",         "%",      ACCENT,     20,  10,   94,   3,120),
}

# =========================
# SBG SIMULATED DATA FIELDS
# (label, unit, color, base, amplitude, period_s)
# =========================
SBG_SIM = {
    "roll":             ("Roll",             "°",     "#38bdf8",  0,    8,   20),
    "pitch":            ("Pitch",            "°",     "#38bdf8",  0,    4,   15),
    "yaw":              ("Yaw / Heading",    "°",     "#38bdf8",  90,  45,   60),
    "gyro_x":           ("Gyro X",           "°/s",   "#a78bfa",  0,   0.8,  8),
    "gyro_y":           ("Gyro Y",           "°/s",   "#a78bfa",  0,   0.5,  6),
    "gyro_z":           ("Gyro Z",           "°/s",   "#a78bfa",  0,   0.3, 10),
    "accel_x":          ("Accel X",          "m/s²",  "#fb923c",  0,   0.4,  7),
    "accel_y":          ("Accel Y",          "m/s²",  "#fb923c",  0,   0.3,  9),
    "accel_z":          ("Accel Z",          "m/s²",  "#fb923c", -9.81,0.15,12),
    "vel_north":        ("Velocity North",   "m/s",   "#34d399",  0.8, 0.3, 18),
    "vel_east":         ("Velocity East",    "m/s",   "#34d399",  0,   0.2, 14),
    "vel_down":         ("Velocity Down",    "m/s",   "#34d399",  0,   0.1, 22),
    "latitude":         ("Latitude",         "°",     "#facc15", -37.9140, 0.0001, 40),
    "longitude":        ("Longitude",        "°",     "#facc15",  145.1340, 0.0001, 50),
    "altitude":         ("Altitude",         "m",     "#facc15",  82,   0.5, 30),
    "solution_mode":    ("Solution Mode",    "",      ACCENT,     None, None, None),
    "gps_fix":          ("GPS Fix",          "",      ACCENT,     None, None, None),
    "num_svs":          ("Satellites",       "",      ACCENT,     12,   2,   35),
    "heading_accuracy": ("Heading Accuracy", "°",     "#fb923c",  0.2,  0.05, 25),
    "position_accuracy":("Pos Accuracy",     "m",     "#fb923c",  0.8,  0.3,  20),
}

TX_COMMANDS = [
    ("tbm/operation_mode",    "MODE_AUTO"),
    ("tbm/cutterhead",        "speed_increase"),
    ("tbm/mobility",          "FORWARD"),
    ("tbm/conveyer",          "CONVEYOR_ON"),
    ("tbm/cutterhead",        "slow_spin"),
    ("tbm/operation_mode",    "MODE_MANUAL"),
    ("tbm/mobility",          "STOP"),
    ("tbm/startup_procedure", "START_READY"),
    ("tbm/EMERGENCY_STOP",    "SAFE_MODE"),
    ("stm32/led",             "YELLOW LED"),
]

PHASES = [
    "SYSTEM INITIALISING",
    "HYDRAULICS PRESSURISING",
    "CUTTERHEAD SPIN-UP",
    "FULL BORING OPERATION",
    "RING BUILD PAUSE",
    "RESUMING ADVANCE",
]

MAX_LOG_LINES = 500


# ==================================================
# HELPERS
# ==================================================
def _resource_path(relative_path):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)


def _load_image(rel_path, size):
    """Load image via PIL if available, return PhotoImage or None."""
    if not PIL_AVAILABLE:
        return None
    path = _resource_path(rel_path)
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# ==================================================
# ATTITUDE INDICATOR DRAW  (self-contained, no global state)
# ==================================================
def _draw_attitude(canvas, roll_deg, pitch_deg, yaw_deg):
    canvas.delete("all")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 10 or h < 10:
        return

    cx, cy = w // 2, h // 2
    r = min(cx, cy) - 8

    roll  = math.radians(roll_deg)
    pitch = pitch_deg
    sin_r, cos_r = math.sin(roll), math.cos(roll)

    horizon_offset = pitch * (r / 45.0)

    # Sky
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#1e3a5f", outline="")

    # Horizon endpoints
    hx1 = cx - r * cos_r
    hy1 = cy - r * sin_r + horizon_offset * cos_r
    hx2 = cx + r * cos_r
    hy2 = cy + r * sin_r - horizon_offset * cos_r

    # Ground polygon
    steps = 64
    ground_pts = [hx1, hy1, hx2, hy2]
    for i in range(steps + 1):
        angle = math.pi * i / steps
        ground_pts += [cx + r * math.cos(angle + math.pi),
                       cy + r * math.sin(angle + math.pi)]
    canvas.create_polygon(ground_pts, fill="#5c3d1a", outline="")

    # Horizon line
    canvas.create_line(hx1, hy1, hx2, hy2, fill="white", width=2)

    # Pitch ladder
    for deg in range(-30, 31, 10):
        if deg == 0:
            continue
        offset = (deg + pitch) * (r / 45.0)
        lw = r * 0.35 if deg % 20 == 0 else r * 0.2
        x1 = cx - lw * cos_r + offset * sin_r
        y1 = cy - lw * sin_r - offset * cos_r
        x2 = cx + lw * cos_r + offset * sin_r
        y2 = cy + lw * sin_r - offset * cos_r
        canvas.create_line(x1, y1, x2, y2, fill="white", width=1)
        canvas.create_text(x2 + 6 * cos_r, y2 + 6 * sin_r,
                           text=str(abs(deg)), fill="white", font=("Segoe UI", 7))

    # Roll arc + ticks
    arc_r = r - 6
    canvas.create_arc(cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                      start=0, extent=180, style="arc", outline="#aaaaaa", width=1)
    for td in [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]:
        a = math.radians(90 - td)
        canvas.create_line(cx + (arc_r - 6) * math.cos(a),
                           cy - (arc_r - 6) * math.sin(a),
                           cx + arc_r * math.cos(a),
                           cy - arc_r * math.sin(a),
                           fill="#aaaaaa", width=1)

    # Roll indicator triangle
    tri_a = math.radians(90) - roll
    tip_x = cx + (arc_r - 12) * math.cos(tri_a)
    tip_y = cy - (arc_r - 12) * math.sin(tri_a)
    la = tri_a + math.radians(10)
    ra = tri_a - math.radians(10)
    canvas.create_polygon(tip_x, tip_y,
                          cx + arc_r * math.cos(la), cy - arc_r * math.sin(la),
                          cx + arc_r * math.cos(ra), cy - arc_r * math.sin(ra),
                          fill="white", outline="")

    # Aircraft symbol
    canvas.create_line(cx - r*0.4, cy, cx - r*0.15, cy, fill="#facc15", width=3)
    canvas.create_line(cx + r*0.15, cy, cx + r*0.4, cy, fill="#facc15", width=3)
    canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#facc15", outline="")
    canvas.create_line(cx, cy, cx, cy - r*0.12, fill="#facc15", width=3)

    # Bezel
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#374151", width=3)

    # Readouts
    canvas.create_text(cx, cy + r + 14,
                       text=f"HDG  {yaw_deg:.1f}°",
                       fill="#38bdf8", font=("Segoe UI", 9, "bold"))
    canvas.create_text(cx - r + 2, cy + r + 14,
                       text=f"R {roll_deg:.1f}°",
                       fill="#a78bfa", font=("Segoe UI", 8), anchor="w")
    canvas.create_text(cx + r, cy + r + 14,
                       text=f"P {pitch_deg:.1f}°",
                       fill="#a78bfa", font=("Segoe UI", 8), anchor="e")


# ==================================================
# DEMO SBG PANEL  (self-contained Toplevel)
# ==================================================
def _open_demo_sbg_panel(win, sim):
    """Open SBG panel populated with simulated data — no real hardware needed."""
    sbg_win = tk.Toplevel(win)
    sbg_win.title("SBG Ellipse-A  —  IMU Data  (DEMO)")
    sbg_win.geometry("1000x820")
    sbg_win.configure(bg=BG_MAIN)

    # ---- Header ----
    hdr = tk.Frame(sbg_win, bg=BG_PANEL, height=60)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)

    # SBG logo
    logo_photo = _load_image("GUI_images/sbg_logo.png", (120, 40))
    if logo_photo:
        lbl = tk.Label(hdr, image=logo_photo, bg=BG_PANEL)
        lbl.image = logo_photo
        lbl.pack(side="left", padx=16, pady=10)
    else:
        tk.Label(hdr, text="SBG SYSTEMS", fg="#38bdf8", bg=BG_PANEL,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=16)

    tk.Label(hdr, text="Ellipse-A  |  IMU / AHRS DATA",
             fg="white", bg=BG_PANEL,
             font=("Segoe UI", 13, "bold")).pack(side="left", padx=8)

    tk.Label(hdr, text="  🎬 SIMULATION  ", fg="#14532d", bg="#4ade80",
             font=("Segoe UI", 8, "bold")).pack(side="left", pady=18)

    # Connection dot (always green in demo)
    tk.Label(hdr, text="●", fg=ACCENT, bg=BG_PANEL,
             font=("Segoe UI", 12)).pack(side="right", padx=(0, 12))
    last_lbl = tk.Label(hdr, text="Simulating...", fg="gray", bg=BG_PANEL,
                         font=("Segoe UI", 8))
    last_lbl.pack(side="right", padx=(0, 4))

    # ---- USB connection bar (greyed out — demo only) ----
    conn_bar = tk.Frame(sbg_win, bg=BG_CARD)
    conn_bar.pack(fill="x", padx=12, pady=(8, 0))

    tk.Label(conn_bar, text="USB PORT", fg="#374151", bg=BG_CARD,
             font=("Segoe UI", 8, "bold")).pack(side="left", padx=(12, 6), pady=8)
    tk.Label(conn_bar, text="N/A  —  Simulation Mode", fg="#374151", bg=BG_CARD,
             font=("Segoe UI", 8)).pack(side="left", pady=8)
    tk.Label(conn_bar, text="115200 baud  |  8N1", fg="#374151", bg=BG_CARD,
             font=("Segoe UI", 8)).pack(side="right", padx=12)

    # ---- Body ----
    body = tk.Frame(sbg_win, bg=BG_MAIN)
    body.pack(fill="both", expand=True, padx=12, pady=10)
    body.columnconfigure(0, weight=3)
    body.columnconfigure(1, weight=2)
    body.rowconfigure(0, weight=1)

    # Left — scrollable data fields
    left = tk.Frame(body, bg=BG_MAIN)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    lc = tk.Canvas(left, bg=BG_MAIN, highlightthickness=0)
    ls = tk.Scrollbar(left, orient="vertical", command=lc.yview)
    lc.configure(yscrollcommand=ls.set)
    lc.pack(side="left", fill="both", expand=True)
    ls.pack(side="right", fill="y")

    data_frame = tk.Frame(lc, bg=BG_MAIN)
    data_frame.bind("<Configure>",
                    lambda e: lc.configure(scrollregion=lc.bbox("all")))
    _dw = lc.create_window((0, 0), window=data_frame, anchor="nw")
    lc.bind("<Configure>", lambda e: lc.itemconfig(_dw, width=e.width))

    GROUPS = [
        ("🧭  ATTITUDE",        ["roll", "pitch", "yaw"]),
        ("🔄  ANGULAR RATE",    ["gyro_x", "gyro_y", "gyro_z"]),
        ("⚡  ACCELERATION",    ["accel_x", "accel_y", "accel_z"]),
        ("💨  VELOCITY",        ["vel_north", "vel_east", "vel_down"]),
        ("📍  POSITION",        ["latitude", "longitude", "altitude"]),
        ("📶  STATUS",          ["solution_mode", "gps_fix", "num_svs",
                                   "heading_accuracy", "position_accuracy"]),
    ]

    sbg_tile_refs = {}   # key → (val_lbl, unit)

    for group_title, keys in GROUPS:
        sec = tk.Frame(data_frame, bg=BG_CARD)
        sec.pack(fill="x", pady=(8, 0))
        tk.Label(sec, text=group_title, fg="cyan", bg=BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 4))

        gf = tk.Frame(sec, bg=BG_CARD)
        gf.pack(fill="x", padx=8, pady=(0, 10))
        COLS = 3
        for col in range(COLS):
            gf.columnconfigure(col, weight=1)

        for i, key in enumerate(keys):
            if key not in SBG_SIM:
                continue
            label, unit, color, *_ = SBG_SIM[key]
            row, col = divmod(i, COLS)

            tile = tk.Frame(gf, bg=BG_MAIN, padx=8, pady=6)
            tile.grid(row=row, column=col, padx=4, pady=3, sticky="ew")

            tk.Label(tile, text=label, fg="#6b7280", bg=BG_MAIN,
                     font=("Segoe UI", 7)).pack(anchor="w")

            val_lbl = tk.Label(tile,
                               text=f"-- {unit}".strip() if unit else "--",
                               fg=color, bg=BG_MAIN,
                               font=("Segoe UI", 12, "bold"))
            val_lbl.pack(anchor="w")
            tk.Frame(tile, bg=ACCENT, height=2).pack(fill="x", pady=(3, 0))

            sbg_tile_refs[key] = (val_lbl, unit)

    # Right — attitude indicator
    right = tk.Frame(body, bg=BG_MAIN)
    right.grid(row=0, column=1, sticky="nsew")
    right.rowconfigure(1, weight=1)
    right.columnconfigure(0, weight=1)

    tk.Label(right, text="ATTITUDE INDICATOR", fg="cyan", bg=BG_MAIN,
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, pady=(4, 6))

    gyro_card = tk.Frame(right, bg=BG_CARD)
    gyro_card.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    gyro_card.rowconfigure(0, weight=1)
    gyro_card.columnconfigure(0, weight=1)

    gyro_cv = tk.Canvas(gyro_card, bg="#0a0f1e", highlightthickness=0)
    gyro_cv.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    # SBG spec card
    info_card = tk.Frame(right, bg=BG_CARD)
    info_card.grid(row=2, column=0, sticky="ew")
    tk.Label(info_card, text="SBG ELLIPSE-A  SPECS", fg="cyan", bg=BG_CARD,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 4))
    for label, value in [
        ("Roll / Pitch Accuracy", "0.05°  RMS"),
        ("Heading Accuracy",      "0.2°  RMS"),
        ("Gyro Bias",             "0.3°/hr"),
        ("Accel Bias",            "0.05 mg"),
        ("Output Rate",           "up to 200 Hz"),
        ("Interface",             "RS-232 / CAN"),
    ]:
        row = tk.Frame(info_card, bg=BG_CARD)
        row.pack(fill="x", padx=12, pady=1)
        tk.Label(row, text=label, fg="#6b7280", bg=BG_CARD,
                 font=("Segoe UI", 8), width=20, anchor="w").pack(side="left")
        tk.Label(row, text=value, fg=TEXT, bg=BG_CARD,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
    tk.Frame(info_card, bg=BG_CARD, height=8).pack()

    # ---- SBG sim tick — shares parent sim clock ----
    def _sbg_tick():
        if not sbg_win.winfo_exists():
            return

        t = sim["t"]
        vals = {}

        for key, spec in SBG_SIM.items():
            _, unit, color, base, amp, period = spec
            if base is None:
                # String fields
                if key == "solution_mode":
                    vals[key] = "NAV POSITION"
                elif key == "gps_fix":
                    vals[key] = "3D"
                continue
            val = base + amp * math.sin(2 * math.pi * t / period)
            val += random.uniform(-amp * 0.03, amp * 0.03)
            vals[key] = val

            if key in sbg_tile_refs:
                lbl, u = sbg_tile_refs[key]
                lbl.config(text=f"{val:.3f} {u}".strip())

        # String fields
        for key in ("solution_mode", "gps_fix"):
            if key in sbg_tile_refs:
                lbl, u = sbg_tile_refs[key]
                lbl.config(text=vals.get(key, "--"))

        # Satellites (integer)
        if "num_svs" in sbg_tile_refs and "num_svs" in vals:
            lbl, u = sbg_tile_refs["num_svs"]
            lbl.config(text=str(int(vals["num_svs"])))

        # Redraw attitude indicator
        _draw_attitude(gyro_cv,
                       vals.get("roll", 0),
                       vals.get("pitch", 0),
                       vals.get("yaw", 0))

        last_lbl.config(text=f"Updated {time.strftime('%H:%M:%S')}")
        sbg_win.after(500, _sbg_tick)

    sbg_win.after(100, _sbg_tick)
    sbg_win.protocol("WM_DELETE_WINDOW", sbg_win.destroy)


# ==================================================
# MAIN DEMO WINDOW
# ==================================================
def open_demo_window(root_ref):

    win = tk.Toplevel(root_ref)
    win.title("Monash BEST TBM Control Interface👷  —  DEMO / SIMULATION MODE")
    win.geometry("1920x1080")
    win.configure(bg=BG_MAIN)

    sim = {
        "t":           0.0,
        "phase_idx":   0,
        "phase_t":     0.0,
        "phase_dur":   random.uniform(12, 20),
        "tx_timer":    0.0,
        "tx_interval": random.uniform(4, 8),
    }

    # ==========================================
    # HEADER
    # ==========================================
    header = tk.Frame(win, bg=BG_PANEL, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    # Logo
    logo_photo = _load_image("GUI_images/logo.png", (50, 50))
    if logo_photo:
        lbl = tk.Label(header, image=logo_photo, bg=BG_PANEL)
        lbl.image = logo_photo
        lbl.pack(side="left", padx=15)

    tk.Label(header, text="TBM CONTROL SYSTEM",
             fg="white", bg=BG_PANEL,
             font=("Segoe UI", 20, "bold")).pack(side="left", padx=(0, 8))

    tk.Label(header, text="  🎬 SIMULATION MODE  ",
             fg="#14532d", bg="#4ade80",
             font=("Segoe UI", 9, "bold")).pack(side="left", pady=20)

    time_lbl = tk.Label(header, fg="white", bg=BG_PANEL, font=("Segoe UI", 12))
    time_lbl.pack(side="right", padx=20)

    def _clock():
        if win.winfo_exists():
            time_lbl.config(text=time.strftime("%H:%M:%S\n%d/%m/%Y"))
            win.after(1000, _clock)
    _clock()

    # ==========================================
    # MAIN LAYOUT
    # ==========================================
    main = tk.Frame(win, bg=BG_MAIN)
    main.pack(fill="both", expand=True)

    # ==========================================
    # SIDEBAR
    # ==========================================
    sidebar = tk.Frame(main, bg=BG_PANEL, width=220)
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
    nav_button("Control Panel").pack(fill="x")
    nav_button("Button Box").pack(fill="x")

    # SBG IMU button — opens demo SBG panel
    sbg_btn = nav_button("SBG IMU")
    sbg_btn.pack(fill="x")
    sbg_btn.config(command=lambda: _open_demo_sbg_panel(win, sim))

    # Demo Mode button (disabled — already in demo)
    tk.Frame(sidebar, bg="#1e3a1e", height=1).pack(fill="x", pady=8)
    tk.Button(sidebar, text="🎬  Demo Mode",
              bg="#14532d", fg="#4ade80",
              relief="flat", anchor="w",
              padx=20, pady=12,
              font=("Segoe UI", 9, "bold"),
              state="disabled").pack(fill="x")

    # Indicators
    tk.Frame(sidebar, bg="#1e2a3a", height=1).pack(fill="x", pady=8)

    def _indicator(text, green=False):
        row = tk.Frame(sidebar, bg=BG_PANEL)
        row.pack(fill="x", padx=14, pady=3)
        dot = tk.Label(row, text="●",
                       fg=ACCENT if green else "#ef4444",
                       bg=BG_PANEL, font=("Segoe UI", 9))
        dot.pack(side="left")
        tk.Label(row, text=f"  {text}", fg="#6b7280", bg=BG_PANEL,
                 font=("Segoe UI", 8)).pack(side="left")
        return dot

    _indicator("MQTT",       green=True)
    _indicator("Button Box", green=False)
    _indicator("TBM Ready",  green=True)

    # Status card
    tk.Frame(sidebar, bg="#1e2a3a", height=1).pack(fill="x", pady=8)

    card = tk.Frame(sidebar, bg=BG_CARD)
    card.pack(fill="x", padx=10, pady=4)
    tk.Label(card, text="STATUS", fg="gray", bg=BG_CARD,
             font=("Segoe UI", 7)).pack(anchor="w", padx=8, pady=(5, 0))
    tk.Label(card, text="OPERATING", fg=ACCENT, bg=BG_CARD,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=8, pady=(0, 5))

    # ==========================================
    # CONTENT AREA — scrollable
    # ==========================================
    content_outer = tk.Frame(main, bg=BG_MAIN)
    content_outer.pack(side="left", fill="both", expand=True)

    content_canvas = tk.Canvas(content_outer, bg=BG_MAIN, highlightthickness=0)
    content_scroll = tk.Scrollbar(content_outer, orient="vertical",
                                   command=content_canvas.yview)
    content_canvas.configure(yscrollcommand=content_scroll.set)
    content_canvas.pack(side="left", fill="both", expand=True)
    content_scroll.pack(side="right", fill="y")

    content = tk.Frame(content_canvas, bg=BG_MAIN)
    content.bind("<Configure>",
                 lambda e: content_canvas.configure(
                     scrollregion=content_canvas.bbox("all")))
    _cwin = content_canvas.create_window((0, 0), window=content, anchor="nw")
    content_canvas.bind("<Configure>",
                        lambda e: content_canvas.itemconfig(_cwin, width=e.width))

    def _wheel(event):
        content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    content_canvas.bind_all("<MouseWheel>", _wheel)
    win.bind("<Destroy>", lambda e: content_canvas.unbind_all("<MouseWheel>"))

    # ==========================================
    # SENSOR GRID
    # ==========================================
    sgo = tk.Frame(content, bg=BG_CARD)
    sgo.pack(fill="x", padx=15, pady=(12, 0))

    sg_hdr = tk.Frame(sgo, bg=BG_CARD)
    sg_hdr.pack(fill="x", padx=12, pady=(8, 4))
    tk.Label(sg_hdr, text="LIVE SENSOR READINGS", fg="cyan", bg=BG_CARD,
             font=("Segoe UI", 10, "bold")).pack(side="left")

    sensor_grid = tk.Frame(sgo, bg=BG_CARD)
    sensor_grid.pack(fill="x", padx=8, pady=(0, 8))

    SENSOR_COLS = 5
    _tile_refs = {}

    for i, (key, spec) in enumerate(SENSOR_DEFS.items()):
        s_label, unit, color, warn, crit, *_ = spec
        row, col = divmod(i, SENSOR_COLS)
        sensor_grid.columnconfigure(col, weight=1)

        tile = tk.Frame(sensor_grid, bg=BG_MAIN, padx=6, pady=6)
        tile.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
        tk.Label(tile, text=s_label, fg="#6b7280", bg=BG_MAIN,
                 font=("Segoe UI", 7)).pack(anchor="w")
        val_lbl = tk.Label(tile, text=f"-- {unit}", fg=color, bg=BG_MAIN,
                           font=("Segoe UI", 13, "bold"))
        val_lbl.pack(anchor="w")
        tk.Frame(tile, bg=ACCENT, height=3).pack(fill="x", pady=(3, 0))
        _tile_refs[key] = (val_lbl, color, warn, crit, unit)

    # ==========================================
    # CAMERA FEEDS
    # ==========================================
    cam_row = tk.Frame(content, bg=BG_MAIN)
    cam_row.pack(fill="both", expand=True, padx=15, pady=(10, 6))
    cam_row.columnconfigure(0, weight=1)
    cam_row.columnconfigure(1, weight=1)

    def make_camera_panel(parent, col, label):
        frame = tk.Frame(parent, bg=BG_CARD)
        frame.grid(row=0, column=col, sticky="nsew",
                   padx=(0 if col == 0 else 6, 6 if col == 0 else 0))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        hdr = tk.Frame(frame, bg=BG_CARD)
        hdr.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        tk.Label(hdr, text=f"📷  {label}", fg="white", bg=BG_CARD,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(hdr, text="●", fg="#ef4444", bg=BG_CARD,
                 font=("Segoe UI", 12)).pack(side="right", padx=(0, 4))
        tk.Label(hdr, text="No Signal", fg="gray", bg=BG_CARD,
                 font=("Segoe UI", 9)).pack(side="right", padx=(0, 6))
        feed = tk.Canvas(frame, bg="#0a0a0a", highlightthickness=0)
        feed.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)

        def _draw(event=None):
            feed.delete("ph")
            w, h = feed.winfo_width(), feed.winfo_height()
            if w < 2 or h < 2:
                return
            for i in range(0, w, 40):
                feed.create_line(i, 0, i, h, fill="#1a1a2e", tags="ph")
            for j in range(0, h, 40):
                feed.create_line(0, j, w, j, fill="#1a1a2e", tags="ph")
            cx, cy = w // 2, h // 2
            feed.create_line(cx-20, cy, cx+20, cy, fill="#374151", width=2, tags="ph")
            feed.create_line(cx, cy-20, cx, cy+20, fill="#374151", width=2, tags="ph")
            bw, bh = 80, 54
            bx, by = cx - bw//2, cy - bh//2 - 10
            feed.create_rectangle(bx, by, bx+bw, by+bh, outline="#374151", width=2, tags="ph")
            feed.create_oval(cx-16, cy-26, cx+16, cy+2, outline="#374151", width=2, tags="ph")
            feed.create_rectangle(bx+bw-18, by-8, bx+bw-6, by,
                                   outline="#374151", width=2, tags="ph")
            feed.create_text(cx, cy+34, text="CAMERA DISCONNECTED",
                             fill="#4b5563", font=("Segoe UI", 10, "bold"), tags="ph")
            feed.create_text(cx, cy+52, text="Waiting for video source...",
                             fill="#374151", font=("Segoe UI", 8), tags="ph")

        feed.bind("<Configure>", _draw)

    make_camera_panel(cam_row, 0, "CAMERA 1  —  Forward View")
    make_camera_panel(cam_row, 1, "CAMERA 2  —  Cutterhead View")

    # ==========================================
    # LOG PANELS
    # ==========================================
    logs_row = tk.Frame(content, bg=BG_MAIN)
    logs_row.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    logs_row.columnconfigure(0, weight=1)
    logs_row.columnconfigure(1, weight=1)

    # Ethernet Comms Log
    comms_frame = tk.Frame(logs_row, bg=BG_CARD)
    comms_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    comms_hdr = tk.Frame(comms_frame, bg=BG_CARD)
    comms_hdr.pack(fill="x", padx=10, pady=(8, 0))
    tk.Label(comms_hdr, text="⬡  ETHERNET COMMS LOG", fg="#38bdf8", bg=BG_CARD,
             font=("Segoe UI", 11, "bold")).pack(side="left")
    tk.Label(comms_hdr, text="●", fg=ACCENT, bg=BG_CARD,
             font=("Segoe UI", 12)).pack(side="right", padx=(0, 4))
    tk.Label(comms_hdr, text="Connected (DEMO)", fg="gray", bg=BG_CARD,
             font=("Segoe UI", 9)).pack(side="right", padx=(0, 6))
    comms_box = tk.Text(comms_frame, bg=BG_MAIN, fg="#38bdf8",
                        font=("Consolas", 9), wrap="none")
    comms_box.pack(fill="both", expand=True, padx=10, pady=8)
    comms_box.tag_config("rx",   foreground="#38bdf8")
    comms_box.tag_config("tx",   foreground="#a3e635")
    comms_box.tag_config("conn", foreground="#fb923c")

    # Control Log
    ctrl_frame = tk.Frame(logs_row, bg=BG_CARD)
    ctrl_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
    tk.Label(ctrl_frame, text="🎮  CONTROL LOG", fg="#a78bfa", bg=BG_CARD,
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
    ctrl_box = tk.Text(ctrl_frame, bg=BG_MAIN, fg=TEXT,
                       font=("Consolas", 9), wrap="none")
    ctrl_box.pack(fill="both", expand=True, padx=10, pady=8)
    ctrl_box.tag_config("btn",   foreground="#c084fc")
    ctrl_box.tag_config("info",  foreground=TEXT)
    ctrl_box.tag_config("phase", foreground="#facc15")

    # ==========================================
    # LOGGING HELPERS
    # ==========================================
    def _append(box, msg, tag):
        box.insert(tk.END, msg + "\n", tag)
        box.see(tk.END)
        lines = int(box.index("end-1c").split(".")[0])
        if lines > MAX_LOG_LINES:
            box.delete("1.0", f"{lines - MAX_LOG_LINES}.0")

    def _log_comms(msg, tag="rx"):
        _append(comms_box, f"[{time.strftime('%H:%M:%S')}] {msg}", tag)

    def _log_ctrl(msg, tag="info"):
        _append(ctrl_box, f"[{time.strftime('%H:%M:%S')}] {msg}", tag)

    # Seed logs
    _log_comms("[MQTT] Connected to broker 192.168.1.10:1883 (DEMO)", "conn")
    _log_ctrl("[DEMO] Simulation started", "phase")
    _log_ctrl(f"[PHASE] {PHASES[0]}", "phase")

    # ==========================================
    # SIMULATION TICK
    # ==========================================
    def _tick():
        if not win.winfo_exists():
            return

        dt = 0.5
        sim["t"]        += dt
        sim["phase_t"]  += dt
        sim["tx_timer"] += dt
        t = sim["t"]

        # Phase rotation
        if sim["phase_t"] >= sim["phase_dur"]:
            sim["phase_t"]   = 0.0
            sim["phase_dur"] = random.uniform(12, 22)
            sim["phase_idx"] = (sim["phase_idx"] + 1) % len(PHASES)
            _log_ctrl(f"[PHASE] {PHASES[sim['phase_idx']]}", "phase")

        # Sensor tiles
        payload_parts = []
        for key, spec in SENSOR_DEFS.items():
            _, unit, base_color, warn, crit, base, amp, period = spec
            val = base + amp * math.sin(2 * math.pi * t / period)
            val += random.uniform(-amp * 0.04, amp * 0.04)
            val = round(val, 2)
            payload_parts.append((key, val))

            val_lbl, bc, w, c, u = _tile_refs[key]
            try:
                fv = float(val)
                if w > c:
                    clr = "#ef4444" if fv <= c else "#f97316" if fv <= w else bc
                else:
                    clr = "#ef4444" if fv >= c else "#f97316" if fv >= w else bc
            except Exception:
                clr = bc
            val_lbl.config(text=f"{val:.2f} {u}", fg=clr)

        # RX packet in comms log
        short = ", ".join(f"{k}:{v}" for k, v in payload_parts[:4]) + ", ..."
        _log_comms(f"[RX]  tbm/telemetry | {short}", "rx")

        # Random TX command
        if sim["tx_timer"] >= sim["tx_interval"]:
            sim["tx_timer"]    = 0.0
            sim["tx_interval"] = random.uniform(5, 12)
            topic, payload = random.choice(TX_COMMANDS)
            _log_comms(f"[TX]  {topic} | {payload}", "tx")
            _log_ctrl(f"[CMD] {topic.split('/')[-1].upper()} → {payload}", "btn")

        win.after(500, _tick)

    win.after(500, _tick)
    win.protocol("WM_DELETE_WINDOW", win.destroy)