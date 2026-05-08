# this code defines the control panel menu option for the GUI
# it contains code for all buttons and command file links to each button


import tkinter as tk
import GTW_Control_Comms.gtw_mqtt_commands as command

# Theme (match main GUI)
BG_MAIN = "#0f172a"
BG_CARD = "#1f2937"
BG_PANEL = "#111827"

# =========================
# CONTROL PANEL WINDOW
# =========================
def open_control_panel(root):
    panel = tk.Toplevel(root)
    panel.title("TBM Control Panel")
    panel.geometry("600x700")   # increased height
    panel.configure(bg=BG_MAIN)

    tk.Label(panel, text="TBM CONTROL PANEL",
             fg="white", bg=BG_MAIN,
             font=("Segoe UI", 18, "bold")).pack(pady=10)

    # =========================
    # SCROLLABLE CONTAINER
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

    # Keep the inner scroll_frame width in sync with the canvas width
    def _on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", _on_canvas_resize)

    container = scroll_frame

    # =========================
    # SECTION CREATOR FUNCTION 
    # =========================
    def create_section(title, num_cols=3):
        frame = tk.Frame(container, bg=BG_CARD)
        frame.pack(fill="x", pady=8)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text=title,
                 fg="cyan", bg=BG_CARD,
                 font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        inner = tk.Frame(frame, bg=BG_CARD)
        inner.pack(fill="x", padx=10, pady=10)

        # Make all columns equal weight so buttons stretch evenly
        for col in range(num_cols):
            inner.columnconfigure(col, weight=1)

        return inner

    # ===========================================================================
    # ========================= SAFETY CONTROL BUTTONS ==========================
    # ===========================================================================
    def safety_control_button(parent, text, status, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.emergency_mode(status)
        )
    
    sec = create_section("SAFETY COMMANDS", num_cols=3)
    safety_control_button(sec, "EMERGENCY STOP", "EMERGENCY_STOP", "red").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    safety_control_button(sec, "SAFE MODE", "SAFE_MODE", "green" ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    safety_control_button(sec, "CLEAR EMERGENCY", "CLEAR EMERGENCY", "orange" ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # ===========================================================================
    # ========================= STARTUP PROCEDURE BUTTONS =======================
    # ===========================================================================
    def system_init_button(parent, text, state, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.system_start_int_mode(state)
        )
    

    sec = create_section("STARTUP COMMANDS", num_cols=2)
    system_init_button(sec, "INITIALIZE", "INITIALIZE", "orange").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    system_init_button(sec, "START SYSTEM", "START_READY", "green").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # ===========================================================================
    # ========================= OPERATION MODE BUTTONS ==========================
    # ===========================================================================
    def operation_mode_button(parent, text, mode, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.operation_mode(mode)
        )

    sec = create_section("OPERATION MODE", num_cols=3)
    operation_mode_button(sec, "MANUAL", "MODE_MANUAL", "orange").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    operation_mode_button(sec, "AUTO", "MODE_AUTO", "blue").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    operation_mode_button(sec, "SAFE IDLE", "MODE_SAFE", "green").grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # ===========================================================================
    # ========================= MOBILITY CONTROL BUTTONS ========================
    # ===========================================================================
    def mobility_control_button(parent, text, direction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.mobility_commands(direction)
        )
    
    sec = create_section("MOBILITY CONTROL", num_cols=3)

    mobility_control_button(sec, "FORWARD", "FORWARD", "yellow").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    mobility_control_button(sec, "LEFT", "LEFT", "blue").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    mobility_control_button(sec, "STOP", "STOP", "red").grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    mobility_control_button(sec, "RIGHT", "RIGHT", "pink").grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    # ===========================================================================
    # ========================= CUTTERHEAD CONTROL BUTTONS ========================
    # ===========================================================================
    def cutterhead_control_button(parent, text, instruction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.cutterhead_control(instruction)
        )
    
    sec = create_section("CUTTERHEAD CONTROL", num_cols=4)

    # cutterhead lockout commands
    cutterhead_control_button(sec, "ACTIVE", "active","green").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    cutterhead_control_button(sec, "DEACTIVATE", "deactivate","red").grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # cutterhead spin commands
    cutterhead_control_button(sec, "Slow Spin", "slow_spin","pink").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    cutterhead_control_button(sec, "speed increase", "speed_increase","green").grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    cutterhead_control_button(sec, "speed decrease", "speed_decrease","yellow").grid(row=1, column=2, padx=5, pady=5, sticky="ew")
    cutterhead_control_button(sec, "stop spin", "stop_spin","red").grid(row=1, column=3, padx=5, pady=5, sticky="ew")


    # =======================================================================
    # ========================= CONVEYOR CONTROL BUTTONS ====================
    # =======================================================================
    def conveyer_control_button(parent, text, instruction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.conveyer_control(instruction)
        )
    
    sec = create_section("CONVEYOR CONTROL", num_cols=2)
    conveyer_control_button(sec, "CONVEYOR_START", "CONVEYOR_ON","green").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    conveyer_control_button(sec, "CONVEYOR_STOP", "CONVEYOR_OFF","red").grid(row=0, column=1, padx=5, pady=5, sticky="ew")






    # =======================================================================
    # ========================== H7 TESTING BAY :) ==========================
    # =======================================================================


    # =======================================================================
    # ========================= LED CONTROL BUTTONS =========================
    # =======================================================================
    def led_control_button(parent, text, status, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.set_led(status)
        )

    sec = create_section("LED CONTROL", num_cols=2)
    led_control_button(sec, "YELLOW LED", "YELLOW LED", "yellow").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    led_control_button(sec, "RED LED", "RED LED", "red").grid(row=0, column=1, padx=5, pady=5, sticky="ew")






    # ======================================================================================================================================================
    # =================================================================== NOTES SECTION ====================================================================
    # ======================================================================================================================================================

    # NOTES
    # =========================
    # BUTTON SPAWN FUNCTION - FOR REFERENCE NOT NEEDED SINCE WE HAVE UNIQUE COMMANDS FOR EACH CATEGORY OF COMMAND
    # =========================
    # def cmd_btn(parent, text, cmd, color=BG_PANEL):
    #     return tk.Button(parent,
    #                      text=text,
    #                      width=16,
    #                      height=2,
    #                      bg=color,
    #                      fg="white",
    #                      relief="flat",
    #                      # the command will be specific to each function and is defined in the mqtt control file
    #                      # here is the placeholder send_command wiht a single param
    #                      command=lambda: command.send_command(cmd))

    # EXAMPLE USE
    # cmd_btn(sec, "EMERGENCY STOP", "EMERGENCY_STOP", "red").grid(row=0, column=0, padx=5, pady=5)