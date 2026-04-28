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

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    container = scroll_frame

    # =========================
    # SECTION CREATOR FUNCTION 
    # =========================
    def create_section(title):
        frame = tk.Frame(container, bg=BG_CARD)
        frame.pack(fill="x", pady=8)

        tk.Label(frame, text=title,
                 fg="cyan", bg=BG_CARD,
                 font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        inner = tk.Frame(frame, bg=BG_CARD)
        inner.pack(padx=10, pady=10)

        return inner

    # ===========================================================================
    # ========================= SAFETY CONTROL BUTTONS ==========================
    # ===========================================================================
    def safety_control_button(parent, text, status, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.emergency_mode(status)
        )
    
    sec = create_section("SAFETY COMMANDS")
    safety_control_button(sec, "EMERGENCY STOP", "EMERGENCY_STOP", "red").grid(row=0, column=0, padx=5, pady=5)
    safety_control_button(sec, "SAFE MODE", "SAFE_MODE", "green" ).grid(row=0, column=1, padx=5, pady=5)
    safety_control_button(sec, "CLEAR EMERGENCY", "CLEAR EMERGENCY", "orange" ).grid(row=0, column=2, padx=5, pady=5)

    # ===========================================================================
    # ========================= STARTUP PROCEDURE BUTTONS =======================
    # ===========================================================================
    def system_init_button(parent, text, state, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.system_start_int_mode(state)
        )
    

    sec = create_section("STARTUP COMMANDS")
    system_init_button(sec, "INITIALIZE", "INITIALIZE", "orange").grid(row=0, column=0, padx=5, pady=5)
    system_init_button(sec, "START SYSTEM", "START_READY", "green").grid(row=0, column=1, padx=5, pady=5)

    # ===========================================================================
    # ========================= OPERATION MODE BUTTONS ==========================
    # ===========================================================================
    def operation_mode_button(parent, text, mode, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.operation_mode(mode)
        )

    sec = create_section("OPERATION MODE")
    operation_mode_button(sec, "MANUAL", "MODE_MANUAL", "orange").grid(row=0, column=0, padx=5, pady=5)
    operation_mode_button(sec, "AUTO", "MODE_AUTO", "blue").grid(row=0, column=1, padx=5, pady=5)
    operation_mode_button(sec, "SAFE IDLE", "MODE_SAFE", "green").grid(row=0, column=2, padx=5, pady=5)

    # ===========================================================================
    # ========================= MOBILITY CONTROL BUTTONS ========================
    # ===========================================================================
    def mobility_control_button(parent, text, direction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.mobility_commands(direction)
        )
    
    sec = create_section("MOBILITY CONTROL")

    mobility_control_button(sec, "FORWARD", "FORWARD", "yellow").grid(row=0, column=1, padx=5, pady=5)
    mobility_control_button(sec, "LEFT", "LEFT", "blue").grid(row=1, column=0, padx=5, pady=5)
    mobility_control_button(sec, "STOP", "STOP", "red").grid(row=1, column=1, padx=5, pady=5)
    mobility_control_button(sec, "RIGHT", "RIGHT", "pink").grid(row=1, column=2, padx=5, pady=5)

    # ===========================================================================
    # ========================= CUTTERHEAD CONTROL BUTTONS ========================
    # ===========================================================================
    def cutterhead_control_button(parent, text, instruction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.cutterhead_control(instruction)
        )
    
    sec = create_section("CUTTERHEAD CONTROL")

    # cutterhead lockout commands
    cutterhead_control_button(sec, "ACTIVE", "active","green").grid(row=0, column=1, padx=5, pady=5)
    cutterhead_control_button(sec, "DEACTIVATE", "deactivate","red").grid(row=0, column=2, padx=5, pady=5)

    # cutterhead spin commands
    # add start slow rotate
    cutterhead_control_button(sec, "Slow Spin", "slow_spin","pink").grid(row=1, column=0, padx=5, pady=5)
    # add speed increase
    cutterhead_control_button(sec, "speed increase", "speed_increase","green").grid(row=1, column=1, padx=5, pady=5)
    # add speed decrease
    cutterhead_control_button(sec, "speed decrease", "speed_decrease","yellow").grid(row=1, column=2, padx=5, pady=5)
    # add stop cutterhead
    cutterhead_control_button(sec, "stop spin", "stop_spin","red").grid(row=1, column=3, padx=5, pady=5)


    # =======================================================================
    # ========================= CONVEYOR CONTROL BUTTONS ====================
    # =======================================================================
    def conveyer_control_button(parent, text, instruction, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.conveyer_control(instruction)
        )
    
    sec = create_section("CONVEYOR CONTROL")
    conveyer_control_button(sec, "CONVEYOR_START", "CONVEYOR_ON","green").grid(row=0, column=0, padx=5, pady=5)
    conveyer_control_button(sec, "CONVEYOR_STOP", "CONVEYOR_OFF","red").grid(row=0, column=1, padx=5, pady=5)






    # =======================================================================
    # ========================== H7 TESTING BAY :) ==========================
    # =======================================================================


    # =======================================================================
    # ========================= LED CONTROL BUTTONS =========================
    # =======================================================================
    def led_control_button(parent, text, status, colour=BG_PANEL):
        return tk.Button(parent,
                text=text,
                width=16,
                height=2,
                bg=colour,
                fg="black",
                relief="flat",
                command=lambda: command.set_led(status)
        )



    sec = create_section("LED CONTROL")
    led_control_button(sec, "YELLOW LED",colour="yellow",status = "yellow").grid(row=0, column=0, padx=5, pady=5)
    led_control_button(sec, "RED LED",colour="red",status = "red").grid(row=0, column=1, padx=5, pady=5)






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