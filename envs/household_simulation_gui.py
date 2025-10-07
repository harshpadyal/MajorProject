import tkinter as tk
import random
import math

class HouseholdSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home HVAC Simulation")
        self.root.geometry("650x550")
        self.root.configure(bg="#1e1e1e")

        # Variables
        self.outdoor_temp = 30
        self.indoor_temp = 24
        self.fan_speed = 0
        self.bulb_on = False
        self.ac_speed = 0       # 0 = off, 1-3 speeds
        self.heater_speed = 0   # 0 = off, 1-3 speeds

        # Create UI
        self.create_ui()

        # Update simulation
        self.update_simulation()

    def create_ui(self):
        # Title
        tk.Label(self.root, text="Smart Home HVAC System", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)

        # Temperature label
        self.temp_label = tk.Label(self.root, text="", font=("Arial", 14), bg="#1e1e1e", fg="white")
        self.temp_label.pack(pady=5)

        # Bulb
        self.bulb_canvas = tk.Canvas(self.root, width=100, height=100, bg="#1e1e1e", highlightthickness=0)
        self.bulb_canvas.pack(pady=10)
        self.bulb_circle = self.bulb_canvas.create_oval(20, 20, 80, 80, fill="gray")

        # Fan
        self.fan_canvas = tk.Canvas(self.root, width=100, height=100, bg="#1e1e1e", highlightthickness=0)
        self.fan_canvas.pack(pady=10)
        self.fan_blades = [
            self.fan_canvas.create_line(50, 50, 50, 10, fill="cyan", width=4),
            self.fan_canvas.create_line(50, 50, 90, 50, fill="cyan", width=4),
            self.fan_canvas.create_line(50, 50, 50, 90, fill="cyan", width=4),
            self.fan_canvas.create_line(50, 50, 10, 50, fill="cyan", width=4),
        ]

        # AC indicator
        self.ac_canvas = tk.Canvas(self.root, width=120, height=50, bg="#1e1e1e", highlightthickness=0)
        self.ac_canvas.pack(pady=5)
        self.ac_rect = self.ac_canvas.create_rectangle(10, 10, 110, 40, fill="gray")
        self.ac_label = self.ac_canvas.create_text(60, 25, text="AC: OFF", fill="white", font=("Arial", 12, "bold"))

        # Heater indicator
        self.heater_canvas = tk.Canvas(self.root, width=120, height=50, bg="#1e1e1e", highlightthickness=0)
        self.heater_canvas.pack(pady=5)
        self.heater_rect = self.heater_canvas.create_rectangle(10, 10, 110, 40, fill="gray")
        self.heater_label = self.heater_canvas.create_text(60, 25, text="Heater: OFF", fill="white", font=("Arial", 12, "bold"))

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12), bg="#1e1e1e", fg="white")
        self.status_label.pack(pady=5)

        # Control buttons
        control_frame = tk.Frame(self.root, bg="#1e1e1e")
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="Toggle Bulb", command=self.toggle_bulb).grid(row=0, column=0, padx=10)
        tk.Button(control_frame, text="Fan Speed +", command=self.increase_fan_speed).grid(row=0, column=1, padx=10)
        tk.Button(control_frame, text="Fan Off", command=self.fan_off).grid(row=0, column=2, padx=10)
        tk.Button(control_frame, text="AC Speed +", command=self.increase_ac_speed).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(control_frame, text="AC Off", command=self.ac_off).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(control_frame, text="Heater Speed +", command=self.increase_heater_speed).grid(row=2, column=0, padx=10, pady=5)
        tk.Button(control_frame, text="Heater Off", command=self.heater_off).grid(row=2, column=1, padx=10, pady=5)

    # --- Control functions ---
    def toggle_bulb(self):
        self.bulb_on = not self.bulb_on
        self.bulb_canvas.itemconfig(self.bulb_circle, fill="yellow" if self.bulb_on else "gray")

    def increase_fan_speed(self):
        self.fan_speed = (self.fan_speed + 1) % 4
        self.status_label.config(text=f"Fan Speed: {self.fan_speed}")

    def fan_off(self):
        self.fan_speed = 0
        self.status_label.config(text="Fan Off")

    def increase_ac_speed(self):
        self.ac_speed = (self.ac_speed + 1) % 4
        self.update_ac_indicator()

    def ac_off(self):
        self.ac_speed = 0
        self.update_ac_indicator()

    def increase_heater_speed(self):
        self.heater_speed = (self.heater_speed + 1) % 4
        self.update_heater_indicator()

    def heater_off(self):
        self.heater_speed = 0
        self.update_heater_indicator()

    # --- Update indicators ---
    def update_ac_indicator(self):
        color = "cyan" if self.ac_speed > 0 else "gray"
        self.ac_canvas.itemconfig(self.ac_rect, fill=color)
        self.ac_canvas.itemconfig(self.ac_label, text=f"AC: {self.ac_speed}")

    def update_heater_indicator(self):
        color = "orange" if self.heater_speed > 0 else "gray"
        self.heater_canvas.itemconfig(self.heater_rect, fill=color)
        self.heater_canvas.itemconfig(self.heater_label, text=f"Heater: {self.heater_speed}")

    # --- Simulation update ---
    def update_simulation(self):
        # Simulate outdoor temp
        self.outdoor_temp += random.uniform(-0.2, 0.2)

        # Update indoor temp based on appliance speeds
        self.indoor_temp += -0.1 * self.ac_speed + 0.1 * self.heater_speed
        self.indoor_temp += 0.02 * (self.outdoor_temp - self.indoor_temp)

        # Rotate fan
        if self.fan_speed > 0:
            self.rotate_fan(5 * self.fan_speed)

        # Update labels
        self.temp_label.config(
            text=f"Indoor Temp: {self.indoor_temp:.1f}°C   |   Outdoor Temp: {self.outdoor_temp:.1f}°C"
        )

        self.update_ac_indicator()
        self.update_heater_indicator()

        self.root.after(100, self.update_simulation)

    # --- Fan rotation ---
    def rotate_fan(self, angle):
        center = (50, 50)
        for blade in self.fan_blades:
            x1, y1, x2, y2 = self.fan_canvas.coords(blade)
            x2r, y2r = self._rotate_point((x2, y2), center, angle)
            self.fan_canvas.coords(blade, center[0], center[1], x2r, y2r)

    def _rotate_point(self, point, center, angle):
        x, y = point
        cx, cy = center
        rad = math.radians(angle)
        dx, dy = x - cx, y - cy
        qx = cx + dx * math.cos(rad) - dy * math.sin(rad)
        qy = cy + dx * math.sin(rad) + dy * math.cos(rad)
        return qx, qy
