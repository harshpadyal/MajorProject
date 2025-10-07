import numpy as np
import matplotlib.pyplot as plt

class HouseholdSimulation:
    def __init__(self):
        # Define environment parameters
        self.indoor_temp = 24.0   # starting indoor temperature (°C)
        self.outdoor_temp = 30.0  # starting outdoor temperature (°C)
        self.desired_temp = 24.0  # user’s desired temperature (°C)
        
        self.bulb_on = False
        self.fan_speed = 0        # 0=off, 1=low, 2=medium, 3=high
        self.ac_on = False
        self.heater_on = False

        # For simulation visualization
        self.time = 0
        self.history = {"time": [], "indoor_temp": [], "outdoor_temp": [], "fan_speed": [], "ac": [], "heater": []}

        self.reset()

    def reset(self):
        self.indoor_temp = 24.0
        self.outdoor_temp = 30.0
        self.fan_speed = 0
        self.ac_on = False
        self.heater_on = False
        self.bulb_on = False
        self.time = 0
        self.history = {"time": [], "indoor_temp": [], "outdoor_temp": [], "fan_speed": [], "ac": [], "heater": []}
        return self._get_state()

    def _get_state(self):
        return np.array([
            self.indoor_temp,
            self.outdoor_temp,
            self.desired_temp
        ])

    def step(self, action):
        """
        action = dict with keys: {'ac', 'heater', 'fan_speed', 'bulb'}
        """

        # Update appliance states
        self.ac_on = action.get("ac", self.ac_on)
        self.heater_on = action.get("heater", self.heater_on)
        self.fan_speed = action.get("fan_speed", self.fan_speed)
        self.bulb_on = action.get("bulb", self.bulb_on)

        # Update outdoor temperature (simulate variation)
        self.outdoor_temp += np.random.uniform(-0.2, 0.2)

        # Temperature change dynamics
        if self.ac_on:
            self.indoor_temp -= 0.3
        if self.heater_on:
            self.indoor_temp += 0.3
        if self.fan_speed > 0:
            self.indoor_temp -= 0.1 * self.fan_speed

        # Gradual influence of outdoor temperature
        self.indoor_temp += 0.05 * (self.outdoor_temp - self.indoor_temp)

        self.time += 1
        self.history["time"].append(self.time)
        self.history["indoor_temp"].append(self.indoor_temp)
        self.history["outdoor_temp"].append(self.outdoor_temp)
        self.history["fan_speed"].append(self.fan_speed)
        self.history["ac"].append(int(self.ac_on))
        self.history["heater"].append(int(self.heater_on))

        reward = -abs(self.indoor_temp - self.desired_temp)
        done = self.time >= 200  # simulation for 200 timesteps
        return self._get_state(), reward, done, {}

    def render(self):
        plt.clf()
        plt.subplot(2, 1, 1)
        plt.plot(self.history["time"], self.history["indoor_temp"], label="Indoor Temp")
        plt.plot(self.history["time"], self.history["outdoor_temp"], label="Outdoor Temp")
        plt.axhline(self.desired_temp, color='gray', linestyle='--', label="Desired Temp")
        plt.legend()
        plt.title("HVAC System Simulation")

        plt.subplot(2, 1, 2)
        plt.plot(self.history["time"], self.history["fan_speed"], label="Fan Speed")
        plt.plot(self.history["time"], self.history["ac"], label="AC On")
        plt.plot(self.history["time"], self.history["heater"], label="Heater On")
        plt.legend()
        plt.xlabel("Time")
        plt.tight_layout()
        plt.pause(0.001)
