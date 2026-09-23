import tkinter as tk
from tkinter import ttk, messagebox
import RPi.GPIO as GPIO
import threading
import time
import glob
import cv2
from PIL import Image, ImageTk

# ==========================================
# BCM PIN CONFIGURATION
# ==========================================
PINS = {
    "M1_CW": 17, "M1_CLK": 18,
    "M2_CW": 27, "M2_CLK": 22,
    "M3_CW": 23, "M3_CLK": 24,
    "RELAY": 25,
    "LIMIT1": 8, "LIMIT2": 6, "LIMIT3": 13,
    "BTS1_RPWM": 26, "BTS2_RPWM": 19
}

class DiagnosticMasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatic Imagery Unit - Hardware & Camera Suite")
        self.root.geometry("1040x720")
        self.root.configure(bg="#1E1E2E")
        self.root.resizable(False, False)

        self.running_motor = False
        self.is_monitoring = True
        self.cap = None

        self.setup_gpio()
        self.create_ui()

        # Start Camera Thread
        self.camera_thread = threading.Thread(target=self.stream_camera, daemon=True)
        self.camera_thread.start()

        # Start Sensor/Switch Monitor Thread
        self.monitor_thread = threading.Thread(target=self.update_sensors, daemon=True)
        self.monitor_thread.start()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Output Pins Setup
        outputs = ["M1_CW", "M1_CLK", "M2_CW", "M2_CLK", "M3_CW", "M3_CLK", "RELAY", "BTS1_RPWM", "BTS2_RPWM"]
        for p in outputs:
            GPIO.setup(PINS[p], GPIO.OUT, initial=GPIO.LOW)

        # Input Pins Setup (Internal Pull-Up)
        inputs = ["LIMIT1", "LIMIT2", "LIMIT3"]
        for p in inputs:
            GPIO.setup(PINS[p], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # PWM setup for BTS7960 Heaters
        self.pwm1 = GPIO.PWM(PINS["BTS1_RPWM"], 1000)
        self.pwm2 = GPIO.PWM(PINS["BTS2_RPWM"], 1000)
        self.pwm1.start(0)
        self.pwm2.start(0)

        # DEFAULT: Turn Relay ON automatically for testing
        GPIO.output(PINS["RELAY"], GPIO.HIGH)

    def create_ui(self):
        # Top Title Header
        title = tk.Label(self.root, text="HARDWARE & CAMERA FULL TESTING SUITE", 
                         font=("Helvetica", 16, "bold"), fg="#89B4FA", bg="#1E1E2E")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#1E1E2E")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # ----------------- LEFT SIDE: CAMERA FEED -----------------
        left_frame = tk.LabelFrame(main_frame, text=" Live Camera Feed ", font=("Helvetica", 11, "bold"),
                                   fg="#CDD6F4", bg="#181825", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.cam_canvas = tk.Label(left_frame, text="Detecting Camera...", font=("Helvetica", 14), 
                                   fg="#A6ADC8", bg="#11111B", width=48, height=22)
        self.cam_canvas.pack(fill=tk.BOTH, expand=True, pady=5)

        # ----------------- RIGHT SIDE: HARDWARE CONTROLS -----------------
        right_frame = tk.Frame(main_frame, bg="#1E1E2E")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))

        # 1. LIVE TEMPERATURE BOX
        temp_box = tk.LabelFrame(right_frame, text=" DS18B20 Temperature ", font=("Helvetica", 10, "bold"),
                                 fg="#CDD6F4", bg="#181825", padx=10, pady=8)
        temp_box.pack(fill=tk.X, pady=4)

        self.lbl_temp = tk.Label(temp_box, text="--.-- °C", font=("Helvetica", 24, "bold"), 
                                 fg="#A6E3A1", bg="#181825")
        self.lbl_temp.pack()

        # 2. RELAY CONTROL BOX
        relay_box = tk.LabelFrame(right_frame, text=" Power Relay Control ", font=("Helvetica", 10, "bold"),
                                  fg="#CDD6F4", bg="#181825", padx=10, pady=8)
        relay_box.pack(fill=tk.X, pady=4)

        self.btn_relay = tk.Button(relay_box, text="RELAY: ON (Active by Default)", font=("Helvetica", 11, "bold"),
                                   bg="#A6E3A1", fg="#11111B", activebackground="#94E2D5", 
                                   command=self.toggle_relay, relief=tk.FLAT, pady=6)
        self.btn_relay.pack(fill=tk.X)

        # 3. STEPPER MOTOR CONTROLS
        motor_box = tk.LabelFrame(right_frame, text=" Stepper Motors (M1, M2, M3) ", font=("Helvetica", 10, "bold"),
                                  fg="#CDD6F4", bg="#181825", padx=10, pady=8)
        motor_box.pack(fill=tk.X, pady=4)

        speed_frame = tk.Frame(motor_box, bg="#181825")
        speed_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(speed_frame, text="Speed:", fg="#CDD6F4", bg="#181825", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=5)

        self.speed_var = tk.StringVar(value="medium")
        for txt, val in [("Fast", "fast"), ("Med", "medium"), ("Slow", "slow")]:
            tk.Radiobutton(speed_frame, text=txt, value=val, variable=self.speed_var,
                           fg="#CDD6F4", bg="#181825", selectcolor="#313244", activebackground="#181825").pack(side=tk.LEFT, padx=3)

        # M1 Controls
        m1_f = tk.Frame(motor_box, bg="#181825")
        m1_f.pack(fill=tk.X, pady=2)
        tk.Label(m1_f, text="M1:", width=4, font=("Helvetica", 9, "bold"), fg="#CDD6F4", bg="#181825").pack(side=tk.LEFT)
        tk.Button(m1_f, text="Forward ▲", bg="#89B4FA", fg="#11111B", command=lambda: self.start_motor("M1", "FWD"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(m1_f, text="Reverse ▼", bg="#CBA6F7", fg="#11111B", command=lambda: self.start_motor("M1", "REV"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # M2 Controls
        m2_f = tk.Frame(motor_box, bg="#181825")
        m2_f.pack(fill=tk.X, pady=2)
        tk.Label(m2_f, text="M2:", width=4, font=("Helvetica", 9, "bold"), fg="#CDD6F4", bg="#181825").pack(side=tk.LEFT)
        tk.Button(m2_f, text="Forward ▲", bg="#89B4FA", fg="#11111B", command=lambda: self.start_motor("M2", "FWD"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(m2_f, text="Reverse ▼", bg="#CBA6F7", fg="#11111B", command=lambda: self.start_motor("M2", "REV"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # M3 Controls
        m3_f = tk.Frame(motor_box, bg="#181825")
        m3_f.pack(fill=tk.X, pady=2)
        tk.Label(m3_f, text="M3:", width=4, font=("Helvetica", 9, "bold"), fg="#CDD6F4", bg="#181825").pack(side=tk.LEFT)
        tk.Button(m3_f, text="Forward ▲", bg="#89B4FA", fg="#11111B", command=lambda: self.start_motor("M3", "FWD"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(m3_f, text="Reverse ▼", bg="#CBA6F7", fg="#11111B", command=lambda: self.start_motor("M3", "REV"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # ALL Motors
        all_f = tk.Frame(motor_box, bg="#181825")
        all_f.pack(fill=tk.X, pady=3)
        tk.Label(all_f, text="ALL:", width=4, font=("Helvetica", 9, "bold"), fg="#CDD6F4", bg="#181825").pack(side=tk.LEFT)
        tk.Button(all_f, text="ALL Forward ▲", bg="#74C7EC", fg="#11111B", command=lambda: self.start_motor("ALL", "FWD"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(all_f, text="ALL Reverse ▼", bg="#F5C2E7", fg="#11111B", command=lambda: self.start_motor("ALL", "REV"), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 4. LIMIT SWITCH INDICATORS
        limit_box = tk.LabelFrame(right_frame, text=" Limit Switches Live Status ", font=("Helvetica", 10, "bold"),
                                  fg="#CDD6F4", bg="#181825", padx=10, pady=8)
        limit_box.pack(fill=tk.X, pady=4)

        sw_f = tk.Frame(limit_box, bg="#181825")
        sw_f.pack(fill=tk.X)
        self.lbl_sw1 = tk.Label(sw_f, text="SW1\nOPEN", width=8, bg="#313244", fg="#F38BA8", font=("Helvetica", 9, "bold"))
        self.lbl_sw1.pack(side=tk.LEFT, expand=True, padx=2)
        self.lbl_sw2 = tk.Label(sw_f, text="SW2\nOPEN", width=8, bg="#313244", fg="#F38BA8", font=("Helvetica", 9, "bold"))
        self.lbl_sw2.pack(side=tk.LEFT, expand=True, padx=2)
        self.lbl_sw3 = tk.Label(sw_f, text="SW3\nOPEN", width=8, bg="#313244", fg="#F38BA8", font=("Helvetica", 9, "bold"))
        self.lbl_sw3.pack(side=tk.LEFT, expand=True, padx=2)

        # 5. BTS7960 HEATERS CONTROL
        bts_box = tk.LabelFrame(right_frame, text=" BTS7960 PWM Heaters ", font=("Helvetica", 10, "bold"),
                                fg="#CDD6F4", bg="#181825", padx=10, pady=8)
        bts_box.pack(fill=tk.X, pady=4)

        b_f = tk.Frame(bts_box, bg="#181825")
        b_f.pack(fill=tk.X)
        self.btn_bts1 = tk.Button(b_f, text="Heater 1: OFF", bg="#313244", fg="#F38BA8", font=("Helvetica", 9, "bold"),
                                  relief=tk.FLAT, command=lambda: self.toggle_bts(1), pady=4)
        self.btn_bts1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)
        self.btn_bts2 = tk.Button(b_f, text="Heater 2: OFF", bg="#313244", fg="#F38BA8", font=("Helvetica", 9, "bold"),
                                  relief=tk.FLAT, command=lambda: self.toggle_bts(2), pady=4)
        self.btn_bts2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

    # ==========================================
    # CAMERA LOGIC (Auto Handles CSI/USB/None)
    # ==========================================
    def stream_camera(self):
        # Attempt to use Picamera2 (for Ribbon Cable Cameras)
        use_picam2 = False
        try:
            from picamera2 import Picamera2
            picam = Picamera2()
            config = picam.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
            picam.configure(config)
            picam.start()
            use_picam2 = True
        except Exception:
            # Fall back to standard OpenCV VideoCapture (USB Webcams)
            self.cap = cv2.VideoCapture(0)

        while self.is_monitoring:
            frame = None
            if use_picam2:
                try:
                    frame = picam.capture_array()
                except Exception:
                    frame = None
            elif self.cap and self.cap.isOpened():
                ret, raw_frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)

            if frame is not None:
                # Resize to fit UI canvas box
                img = Image.fromarray(frame).resize((500, 380))
                imgtk = ImageTk.PhotoImage(image=img)
                self.cam_canvas.imgtk = imgtk
                self.cam_canvas.configure(image=imgtk, text="")
            else:
                self.cam_canvas.configure(image="", text="[ Camera Offline / Not Connected ]\nCheck Ribbon or USB Cable", 
                                          fg="#F38BA8")
                time.sleep(1)
            time.sleep(0.03)

        if use_picam2:
            picam.stop()
        elif self.cap and self.cap.isOpened():
            self.cap.release()

    # ==========================================
    # HARDWARE ACTION HANDLERS
    # ==========================================
    def toggle_relay(self):
        current_state = GPIO.input(PINS["RELAY"])
        new_state = GPIO.LOW if current_state == GPIO.HIGH else GPIO.HIGH
        GPIO.output(PINS["RELAY"], new_state)

        if new_state == GPIO.HIGH:
            self.btn_relay.config(text="RELAY: ON (Active)", bg="#A6E3A1", fg="#11111B")
        else:
            self.btn_relay.config(text="RELAY: OFF (Cut-Off)", bg="#F38BA8", fg="#11111B")

    def toggle_bts(self, num):
        pwm = self.pwm1 if num == 1 else self.pwm2
        btn = self.btn_bts1 if num == 1 else self.btn_bts2

        if "OFF" in btn.cget("text"):
            pwm.ChangeDutyCycle(100)
            btn.config(text=f"Heater {num}: ON", bg="#A6E3A1", fg="#11111B")
        else:
            pwm.ChangeDutyCycle(0)
            btn.config(text=f"Heater {num}: OFF", bg="#313244", fg="#F38BA8")

    def start_motor(self, target, direction):
        if self.running_motor:
            messagebox.showwarning("Busy", "Motor is already moving!")
            return
        threading.Thread(target=self.step_motor_logic, args=(target, direction), daemon=True).start()

    def step_motor_logic(self, target, direction):
        self.running_motor = True
        spd = self.speed_var.get()
        delay = 0.0006 if spd == "fast" else (0.0015 if spd == "medium" else 0.0035)
        steps = 400

        motors = []
        if target == "M1": motors = [(PINS["M1_CW"], PINS["M1_CLK"], PINS["LIMIT1"])]
        elif target == "M2": motors = [(PINS["M2_CW"], PINS["M2_CLK"], PINS["LIMIT2"])]
        elif target == "M3": motors = [(PINS["M3_CW"], PINS["M3_CLK"], PINS["LIMIT3"])]
        elif target == "ALL": motors = [
            (PINS["M1_CW"], PINS["M1_CLK"], PINS["LIMIT1"]),
            (PINS["M2_CW"], PINS["M2_CLK"], PINS["LIMIT2"]),
            (PINS["M3_CW"], PINS["M3_CLK"], PINS["LIMIT3"])
        ]

        dir_val = GPIO.HIGH if direction == "FWD" else GPIO.LOW
        for cw, _, _ in motors:
            GPIO.output(cw, dir_val)

        time.sleep(0.001)

        for _ in range(steps):
            active_clks = []
            for cw, clk, limit in motors:
                # Stop pulse if corresponding limit switch is pressed (Active LOW)
                if GPIO.input(limit) == GPIO.LOW:
                    continue
                active_clks.append(clk)

            if not active_clks:
                break

            for clk in active_clks:
                GPIO.output(clk, GPIO.HIGH)
            time.sleep(delay)
            for clk in active_clks:
                GPIO.output(clk, GPIO.LOW)
            time.sleep(delay)

        self.running_motor = False

    # ==========================================
    # SENSOR & LIMIT SWITCH MONITOR
    # ==========================================
    def update_sensors(self):
        while self.is_monitoring:
            # 1. Update DS18B20 Temp
            t_str = self.read_ds18b20()
            self.lbl_temp.config(text=t_str)

            # 2. Update Limit Switches
            self.sync_switch_badge(self.lbl_sw1, "SW1", GPIO.input(PINS["LIMIT1"]))
            self.sync_switch_badge(self.lbl_sw2, "SW2", GPIO.input(PINS["LIMIT2"]))
            self.sync_switch_badge(self.lbl_sw3, "SW3", GPIO.input(PINS["LIMIT3"]))

            time.sleep(0.3)

    def sync_switch_badge(self, label, name, pin_val):
        if pin_val == GPIO.LOW:
            label.config(text=f"{name}\nTRIGGERED", bg="#A6E3A1", fg="#11111B")
        else:
            label.config(text=f"{name}\nOPEN", bg="#313244", fg="#F38BA8")

    def read_ds18b20(self):
        base_dir = '/sys/bus/w1/devices/'
        try:
            device_folders = glob.glob(base_dir + '28*')
            if not device_folders:
                return "Sensor N/A"
            device_file = device_folders[0] + '/w1_slave'
            with open(device_file, 'r') as f:
                lines = f.readlines()
            if lines[0].strip().endswith('YES'):
                pos = lines[1].find('t=')
                if pos != -1:
                    temp_c = float(lines[1][pos+2:]) / 1000.0
                    return f"{temp_c:.1f} °C"
        except Exception:
            return "Read Error"
        return "--.-- °C"

    def on_close(self):
        self.is_monitoring = False
        self.pwm1.stop()
        self.pwm2.stop()
        GPIO.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosticMasterGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
