import tkinter as tk
import random
import math

class HouseholdSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 1BHK Smart Home Visual Simulation")
        self.root.geometry("1200x850")
        self.root.configure(bg="#1e1e1e")

        self.outdoor_temp = 30
        self.indoor_temp = 25

        # Room states
        self.rooms = {
            "Hall": {
                "lights": [False, False],
                "fans": [0, 0],
                "ac": None,
                "heater": None,
                "tv": False
            },
            "Bedroom": {"light": False, "fan": 0, "ac": None, "heater": None},
            "Kitchen": {"light": False, "fan": 0},
            "Bathroom": {"light": False, "geezer": None},
            "Toilet": {"light": False}
        }

        self.create_ui()
        self.update_simulation()

    # ---------------------------- UI Layout ----------------------------
    def create_ui(self):
        tk.Label(
            self.root, text="🏠 1BHK Smart Home HVAC System",
            font=("Arial", 22, "bold"), bg="#1e1e1e", fg="white"
        ).pack(pady=10)

        self.temp_label = tk.Label(
            self.root, text="", font=("Arial", 14), bg="#1e1e1e", fg="white"
        )
        self.temp_label.pack(pady=5)

        # Create scrollable frame
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.pack(fill="both", expand=True)

        canvas_main = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas_main.yview)
        scrollable_frame = tk.Frame(canvas_main, bg="#1e1e1e")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_main.configure(scrollregion=canvas_main.bbox("all"))
        )

        canvas_main.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_main.configure(yscrollcommand=scrollbar.set)

        canvas_main.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        layout = tk.Frame(scrollable_frame, bg="#1e1e1e")
        layout.pack()

        self.room_canvases = {}
        self.room_visuals = {}

        grid = [
            ("Hall", 0, 0),
            ("Bedroom", 0, 1),
            ("Kitchen", 1, 0),
            ("Bathroom", 1, 1),
            ("Toilet", 2, 0)
        ]

        for room, r, c in grid:
            height = 420 if room == "Hall" else 260
            canvas = tk.Canvas(
                layout, width=550, height=height, bg="#2b2b2b",
                highlightthickness=2, highlightbackground="white"
            )
            canvas.grid(row=r, column=c, padx=20, pady=20)
            self.room_canvases[room] = canvas

            visuals = self.draw_room_visuals(canvas, room)
            self.room_visuals[room] = visuals
            self.add_controls(canvas, room)

    # ---------------------------- Room Visuals ----------------------------
    def draw_room_visuals(self, canvas, room):
        visuals = {}
        x, y = 50, 50

        if "lights" in self.rooms[room]:
            visuals["lights"] = []
            for i in range(len(self.rooms[room]["lights"])):
                bulb = canvas.create_oval(x + i * 50, y, x + 30 + i * 50, y + 30, fill="gray")
                visuals["lights"].append(bulb)
        elif "light" in self.rooms[room]:
            visuals["light"] = canvas.create_oval(x, y, x + 30, y + 30, fill="gray")

        if "fans" in self.rooms[room]:
            visuals["fans"] = []
            for i in range(len(self.rooms[room]["fans"])):
                fan = self.create_fan(canvas, x + 150 + i * 70, y + 40)
                visuals["fans"].append(fan)
        elif "fan" in self.rooms[room]:
            visuals["fan"] = self.create_fan(canvas, x + 150, y + 40)

        if "ac" in self.rooms[room]:
            visuals["ac"] = canvas.create_rectangle(300, y, 370, y + 30, fill="gray")
            visuals["ac_text"] = canvas.create_text(335, y + 15, text="", fill="blue", font=("Arial", 10, "bold"))

        if "heater" in self.rooms[room]:
            visuals["heater"] = canvas.create_rectangle(380, y, 450, y + 30, fill="gray")
            visuals["heater_text"] = canvas.create_text(415, y + 15, text="", fill="red", font=("Arial", 10, "bold"))

        if "geezer" in self.rooms[room]:
            visuals["geezer"] = canvas.create_rectangle(300, y, 360, y + 30, fill="gray")

        if "tv" in self.rooms[room]:
            visuals["tv"] = canvas.create_rectangle(200, 100, 280, 150, fill="gray")
            visuals["tv_text"] = canvas.create_text(240, 125, text="OFF", fill="white", font=("Arial", 10, "bold"))

        canvas.create_text(60, 10, text=room, fill="white", font=("Arial", 14, "bold"))
        return visuals

    def create_fan(self, canvas, cx, cy):
        blades = [
            canvas.create_line(cx, cy, cx, cy - 20, fill="cyan", width=3),
            canvas.create_line(cx, cy, cx + 20, cy, fill="cyan", width=3),
            canvas.create_line(cx, cy, cx, cy + 20, fill="cyan", width=3),
            canvas.create_line(cx, cy, cx - 20, cy, fill="cyan", width=3),
        ]
        return {"center": (cx, cy), "blades": blades}

    # ---------------------------- Controls ----------------------------
    def add_controls(self, canvas, room):
        frame = tk.Frame(canvas, bg="#2b2b2b")
        canvas.create_window(270, 340 if room == "Hall" else 220, window=frame)
        r = self.rooms[room]

        if room == "Hall":
            tk.Button(frame, text="Light 1", command=lambda: self.toggle_single_light(r, room, 0)).grid(row=0, column=0, padx=3)
            tk.Button(frame, text="Light 2", command=lambda: self.toggle_single_light(r, room, 1)).grid(row=0, column=1, padx=3)
            tk.Button(frame, text="Fan 1 +", command=lambda: self.change_single_fan(r, room, 0, +1)).grid(row=1, column=0, padx=3)
            tk.Button(frame, text="Fan 2 +", command=lambda: self.change_single_fan(r, room, 1, +1)).grid(row=1, column=1, padx=3)
            tk.Button(frame, text="Fan 1 Off", command=lambda: self.change_single_fan(r, room, 0, 0)).grid(row=2, column=0, padx=3)
            tk.Button(frame, text="Fan 2 Off", command=lambda: self.change_single_fan(r, room, 1, 0)).grid(row=2, column=1, padx=3)
            tk.Button(frame, text="AC ↓", command=lambda: self.change_temp(r, room, "ac", -1)).grid(row=3, column=0, padx=3)
            tk.Button(frame, text="AC ↑", command=lambda: self.change_temp(r, room, "ac", +1)).grid(row=3, column=1, padx=3)
            tk.Button(frame, text="AC Off", command=lambda: self.turn_off(r, room, "ac")).grid(row=3, column=2, padx=3)
            tk.Button(frame, text="Heater ↑", command=lambda: self.change_temp(r, room, "heater", +1)).grid(row=4, column=0, padx=3)
            tk.Button(frame, text="Heater ↓", command=lambda: self.change_temp(r, room, "heater", -1)).grid(row=4, column=1, padx=3)
            tk.Button(frame, text="Heater Off", command=lambda: self.turn_off(r, room, "heater")).grid(row=4, column=2, padx=3)
            tk.Button(frame, text="Toggle TV", command=lambda: self.toggle_tv(r, room)).grid(row=5, column=0, padx=3)
            return

        if "light" in r:
            tk.Button(frame, text="Toggle Light", command=lambda: self.toggle_light(r, room)).grid(row=0, column=0, padx=3)
        if "fan" in r:
            tk.Button(frame, text="Fan +", command=lambda: self.change_fan_speed(r, room, +1)).grid(row=0, column=1, padx=3)
            tk.Button(frame, text="Fan Off", command=lambda: self.change_fan_speed(r, room, 0)).grid(row=0, column=2, padx=3)
        if "ac" in r:
            tk.Button(frame, text="AC ↓", command=lambda: self.change_temp(r, room, "ac", -1)).grid(row=1, column=0, padx=3)
            tk.Button(frame, text="AC ↑", command=lambda: self.change_temp(r, room, "ac", +1)).grid(row=1, column=1, padx=3)
            tk.Button(frame, text="AC Off", command=lambda: self.turn_off(r, room, "ac")).grid(row=1, column=2, padx=3)
        if "heater" in r:
            tk.Button(frame, text="Heater ↑", command=lambda: self.change_temp(r, room, "heater", +1)).grid(row=2, column=0, padx=3)
            tk.Button(frame, text="Heater ↓", command=lambda: self.change_temp(r, room, "heater", -1)).grid(row=2, column=1, padx=3)
            tk.Button(frame, text="Heater Off", command=lambda: self.turn_off(r, room, "heater")).grid(row=2, column=2, padx=3)
        if "geezer" in r:
            tk.Button(frame, text="Toggle Geezer", command=lambda: self.toggle_geezer(r, room)).grid(row=3, column=0, padx=3)

    # ---------------------------- Device Logic ----------------------------
    def toggle_single_light(self, devices, room, idx):
        devices["lights"][idx] = not devices["lights"][idx]
        self.update_visuals(room)

    def change_single_fan(self, devices, room, idx, val):
        if val == 0:
            devices["fans"][idx] = 0
        else:
            devices["fans"][idx] = min(3, devices["fans"][idx] + 1)
        self.update_visuals(room)

    def toggle_light(self, devices, room):
        devices["light"] = not devices["light"]
        self.update_visuals(room)

    def change_fan_speed(self, devices, room, val):
        if val == 0:
            devices["fan"] = 0
        else:
            devices["fan"] = min(3, devices["fan"] + 1)
        self.update_visuals(room)

    def change_temp(self, devices, room, key, delta):
        if devices[key] is None:
            devices[key] = 26 if key == "ac" else 22
        else:
            if key == "ac":
                devices[key] = max(18, min(30, devices[key] + delta))
            else:
                devices[key] = max(20, min(35, devices[key] + delta))
        self.update_visuals(room)

    def turn_off(self, devices, room, key):
        devices[key] = None
        self.update_visuals(room)

    def toggle_tv(self, devices, room):
        devices["tv"] = not devices["tv"]
        self.update_visuals(room)

    def toggle_geezer(self, devices, room):
        if devices["geezer"] is None:
            devices["geezer"] = 60  # default temperature
        else:
            devices["geezer"] = None
        self.update_visuals(room)

    # ---------------------------- Visual Update ----------------------------
    def update_visuals(self, room):
        r = self.rooms[room]
        c = self.room_canvases[room]
        v = self.room_visuals[room]

        if "lights" in r:
            for i, bulb in enumerate(v["lights"]):
                c.itemconfig(bulb, fill="yellow" if r["lights"][i] else "gray")
        elif "light" in r:
            c.itemconfig(v["light"], fill="yellow" if r["light"] else "gray")

        if "fans" in r:
            for i, fan in enumerate(v["fans"]):
                if r["fans"][i] > 0:
                    self.rotate_fan(c, fan, 5 * r["fans"][i])
        elif "fan" in r:
            if r["fan"] > 0:
                self.rotate_fan(c, v["fan"], 5 * r["fan"])

        if "ac" in r:
            c.itemconfig(v["ac"], fill="cyan" if r["ac"] is not None else "gray")
            if "ac_text" in v:
                c.itemconfig(v["ac_text"], text=str(r["ac"]) if r["ac"] is not None else "")

        if "heater" in r:
            c.itemconfig(v["heater"], fill="orange" if r["heater"] is not None else "gray")
            if "heater_text" in v:
                c.itemconfig(v["heater_text"], text=str(r["heater"]) if r["heater"] is not None else "")

        if "tv" in r and "tv" in v:
            c.itemconfig(v["tv"], fill="green" if r["tv"] else "gray")
            if "tv_text" in v:
                c.itemconfig(v["tv_text"], text="ON" if r["tv"] else "OFF")

        if "geezer" in r and "geezer" in v:
            c.itemconfig(v["geezer"], fill="orange" if r["geezer"] is not None else "gray")

    def rotate_fan(self, canvas, fan, angle):
        cx, cy = fan["center"]
        for blade in fan["blades"]:
            x1, y1, x2, y2 = canvas.coords(blade)
            x2r, y2r = self._rotate_point((x2, y2), (cx, cy), angle)
            canvas.coords(blade, cx, cy, x2r, y2r)

    def _rotate_point(self, point, center, angle):
        x, y = point
        cx, cy = center
        rad = math.radians(angle)
        dx, dy = x - cx, y - cy
        qx = cx + dx * math.cos(rad) - dy * math.sin(rad)
        qy = cy + dx * math.sin(rad) + dy * math.cos(rad)
        return qx, qy

    # ---------------------------- Simulation Loop ----------------------------
    def update_simulation(self):
        self.outdoor_temp += random.uniform(-0.1, 0.1)

        for room, devices in self.rooms.items():
            # AC effect
            if "ac" in devices and devices["ac"] is not None:
                self.indoor_temp += (devices["ac"] - self.indoor_temp) * 0.02

            # Heater effect
            if "heater" in devices and devices["heater"] is not None:
                self.indoor_temp += (devices["heater"] - self.indoor_temp) * 0.02

            # Fan effect (small cooling effect)
            if "fans" in devices:
                total_speed = sum(devices["fans"])
                if total_speed > 0:
                    self.indoor_temp -= 0.05 * total_speed
            elif "fan" in devices and devices["fan"] > 0:
                self.indoor_temp -= 0.05 * devices["fan"]

        # Clamp indoor temperature
        self.indoor_temp = max(15, min(35, self.indoor_temp))

        self.temp_label.config(
            text=f"Indoor: {self.indoor_temp:.1f}°C | Outdoor: {self.outdoor_temp:.1f}°C"
        )

        for room in self.rooms.keys():
            self.update_visuals(room)

        self.root.after(200, self.update_simulation)


if __name__ == "__main__":
    root = tk.Tk()
    app = HouseholdSimulationGUI(root)
    root.mainloop()
