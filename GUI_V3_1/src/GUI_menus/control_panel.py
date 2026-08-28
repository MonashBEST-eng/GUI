# control_panel.py
# TBM Control Panel — laid out as a 5x5 grid of category cards. Each card is
# one control category (Safety, Startup, Operation Mode, ...) built from
# round industrial pushbuttons (see ui_widgets.py), the same visual family
# as the dashboard's E-STOP mushroom button. Categories not yet defined show
# as a dashed placeholder card, ready for future control groups.

import tkinter as tk
import GTW_Control_Comms.gtw_mqtt_commands as command
import GUI_menus.ui_widgets as ui_widgets
import GUI_menus.heartbeat_panel as heartbeat_panel

# Theme (match main GUI)
BG_MAIN  = "#0f172a"
BG_CARD  = "#1f2937"
BG_PANEL = "#111827"

GRID_COLS = 5
GRID_ROWS = 5
CARD_SIZE = 230

# =========================
# CATEGORY DEFINITIONS
# (title, accent color, [ (label, button color, command_fn), ... ])
# Add a new tuple here to fill the next placeholder slot — no layout
# changes needed, the grid just fills in row-major order.
#
# The special string "__HEARTBEAT__" fills a slot with the link-heartbeat
# card (RESUME button, live LED, Test button) instead of a normal button
# category — see _build_heartbeat_card() below.

# to make new category use this
# ("NEW CATEGORY", "#a78bfa", [
#     ("BUTTON\nLABEL", "#22c55e", lambda: command.some_function("ARG")),
# ]),

# =========================
def _categories():
    return [
        ("SAFETY", "#ef4444", [
            ("EMERGENCY\nSTOP",  "#ef4444", lambda: command.emergency_mode("EMERGENCY_STOP")),
            ("SAFE\nMODE",       "#22c55e", lambda: command.emergency_mode("SAFE_MODE")),
            ("CLEAR\nEMERGENCY", "#f97316", lambda: command.emergency_mode("CLEAR EMERGENCY")),
        ]),
        ("STARTUP", "#f97316", [
            ("INITIALIZE",   "#f97316", lambda: command.system_start_int_mode("INITIALIZE")),
            ("START\nSYSTEM", "#22c55e", lambda: command.system_start_int_mode("START_READY")),
        ]),
        ("OPERATION MODE", "#38bdf8", [
            ("MANUAL",    "#f97316", lambda: command.operation_mode("MODE_MANUAL")),
            ("AUTO",      "#38bdf8", lambda: command.operation_mode("MODE_AUTO")),
            ("SAFE\nIDLE", "#22c55e", lambda: command.operation_mode("MODE_SAFE")),
        ]),
        ("MOBILITY", "#facc15", [
            ("FORWARD", "#facc15", lambda: command.mobility_commands("FORWARD")),
            ("LEFT",    "#38bdf8", lambda: command.mobility_commands("LEFT")),
            ("STOP",    "#ef4444", lambda: command.mobility_commands("STOP")),
            ("RIGHT",   "#f472b6", lambda: command.mobility_commands("RIGHT")),
        ]),
        ("CUTTERHEAD", "#a78bfa", [
            ("ACTIVE",      "#22c55e", lambda: command.cutterhead_control("active")),
            ("DEACTIVATE",  "#ef4444", lambda: command.cutterhead_control("deactivate")),
            ("SLOW\nSPIN",  "#f472b6", lambda: command.cutterhead_control("slow_spin")),
            ("SPEED\nUP",   "#22c55e", lambda: command.cutterhead_control("speed_increase")),
            ("SPEED\nDOWN", "#facc15", lambda: command.cutterhead_control("speed_decrease")),
            ("STOP\nSPIN",  "#ef4444", lambda: command.cutterhead_control("stop_spin")),
        ]),
        ("CONVEYOR", "#34d399", [
            ("START",       "#22c55e", lambda: command.conveyer_control("CONVEYOR_ON")),
            ("STOP",        "#ef4444", lambda: command.conveyer_control("CONVEYOR_OFF")),
            ("FORWARD",     "#38bdf8", lambda: command.conveyer_control("FORWARD")),
            ("REVERSE",     "#f472b6", lambda: command.conveyer_control("REVERSE")),
            ("SPEED\nLOW",  "#facc15", lambda: command.conveyer_control("SPEED_LOW")),
            ("SPEED\nMED",  "#facc15", lambda: command.conveyer_control("SPEED_MED")),
            ("SPEED\nHIGH", "#facc15", lambda: command.conveyer_control("SPEED_HIGH")),
        ]),
        ("LED (H7 TEST)", "#facc15", [
            ("YELLOW\nLED", "#facc15", lambda: command.set_led("YELLOW LED")),
            ("RED\nLED",    "#ef4444", lambda: command.set_led("RED LED")),
        ]),
        "__HEARTBEAT__",
    ]


# =========================
# CARD BUILDERS
# =========================
def _build_category_card(parent, row, col, title, accent, buttons):
    card = tk.Frame(parent, bg=BG_CARD, width=CARD_SIZE, height=CARD_SIZE,
                    highlightbackground=accent, highlightthickness=1)
    card.grid(row=row, column=col, padx=8, pady=8)
    card.grid_propagate(False)

    tk.Frame(card, bg=accent, height=4).pack(fill="x")
    tk.Label(card, text=title, fg=accent, bg=BG_CARD,
             font=("Segoe UI", 10, "bold")).pack(pady=(10, 6))

    btn_area = tk.Frame(card, bg=BG_CARD)
    btn_area.pack(expand=True)

    cols = 3 if len(buttons) > 4 else 2
    for i, (label, color, cmd) in enumerate(buttons):
        r, c = divmod(i, cols)
        btn = ui_widgets.make_industrial_button(btn_area, label, color, cmd, size=60, bg=BG_CARD)
        btn.grid(row=r, column=c, padx=6, pady=6)


def _build_heartbeat_card(parent, row, col):
    """Link-heartbeat card: RESUME button (clears a tripped heartbeat
    fault and the E-STOP it triggers), a live flashing heartbeat LED, and
    a button that genuinely tests the deadman's-switch path end-to-end.
    Same card frame/sizing as the button categories, just yellow-accented
    (matching the heartbeat's own warning-color theme) and built from
    heartbeat_panel's own widgets instead of round industrial buttons."""
    card = tk.Frame(parent, bg=BG_CARD, width=CARD_SIZE, height=CARD_SIZE,
                    highlightbackground="#facc15", highlightthickness=1)
    card.grid(row=row, column=col, padx=8, pady=8)
    card.grid_propagate(False)

    tk.Frame(card, bg="#facc15", height=4).pack(fill="x")
    tk.Label(card, text="LINK HEARTBEAT", fg="#facc15", bg=BG_CARD,
             font=("Segoe UI", 10, "bold")).pack(pady=(10, 6))

    content = tk.Frame(card, bg=BG_CARD)
    content.pack(expand=True)

    heartbeat_panel.create_resume_widget(content, size=90, bg=BG_CARD).pack(pady=(0, 12))
    heartbeat_panel.create_heartbeat_indicator(content, bg=BG_CARD).pack(pady=(0, 12))
    heartbeat_panel.create_test_button(content, bg=BG_CARD).pack()


def _build_placeholder_card(parent, row, col):
    card = tk.Frame(parent, bg=BG_MAIN, width=CARD_SIZE, height=CARD_SIZE,
                    highlightbackground="#1e2a3a", highlightthickness=1)
    card.grid(row=row, column=col, padx=8, pady=8)
    card.grid_propagate(False)

    inner = tk.Frame(card, bg=BG_MAIN)
    inner.place(relx=0.5, rely=0.5, anchor="center")

    ui_widgets.make_placeholder_slot(inner, size=64).pack()
    tk.Label(inner, text="FUTURE\nCONTROL CATEGORY", fg="#374151", bg=BG_MAIN,
             font=("Segoe UI", 8, "bold"), justify="center").pack(pady=(8, 0))


# =========================
# PANEL WINDOW
# =========================
def open_control_panel(root):
    panel = tk.Toplevel(root)
    panel.title("TBM Control Panel")
    panel.geometry("1350x1200")
    panel.configure(bg=BG_MAIN)

    tk.Label(panel, text="TBM CONTROL PANEL",
             fg="white", bg=BG_MAIN,
             font=("Segoe UI", 18, "bold")).pack(pady=10)

    # =========================
    # SCROLLABLE CONTAINER (in case the window is resized smaller)
    # =========================
    canvas = tk.Canvas(panel, bg=BG_MAIN, highlightthickness=0)
    scrollbar = tk.Scrollbar(panel, orient="vertical", command=canvas.yview)

    scroll_frame = tk.Frame(canvas, bg=BG_MAIN)
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", _on_canvas_resize)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    panel.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # =========================
    # 5x5 CATEGORY GRID
    # =========================
    grid_container = tk.Frame(scroll_frame, bg=BG_MAIN)
    grid_container.pack(padx=12, pady=6)

    categories = _categories()
    total_cells = GRID_ROWS * GRID_COLS
    while len(categories) < total_cells:
        categories.append(None)   # placeholder marker for an empty slot

    for i, cat in enumerate(categories[:total_cells]):
        row, col = divmod(i, GRID_COLS)
        if cat is None:
            _build_placeholder_card(grid_container, row, col)
        elif cat == "__HEARTBEAT__":
            _build_heartbeat_card(grid_container, row, col)
        else:
            title, accent, buttons = cat
            _build_category_card(grid_container, row, col, title, accent, buttons)