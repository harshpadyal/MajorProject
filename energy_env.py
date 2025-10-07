# energy_env.py
import numpy as np
import gymnasium as gym
from gymnasium import spaces

class EnergyEnv(gym.Env):
    """
    Simple 24-step (hour) energy scheduling environment.
    - 3 deferrable appliances: washer (1h), water_heater (1h), ev (4h)
    - fridge: always-on load
    - price: TOU tariff (cheap at night, expensive in evening)
    - action: start appliance [0/1] vector
    - reward: negative electricity cost
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.horizon = 24
        self.appliances = {
            "washer": {"power": 1.0, "duration": 1},
            "water":  {"power": 1.5, "duration": 1},
            "ev":     {"power": 3.0, "duration": 4}
        }
        self.names = list(self.appliances.keys())
        self.n_appliances = len(self.names)
        self.fridge_power = 0.2  # always on

        # TOU price: ₹0.5 at night, ₹2.0 at evening peak, ₹1.0 otherwise
        self.price = np.array([
            0.5 if (h < 6 or h >= 22) else
            2.0 if (17 <= h <= 21) else
            1.0
            for h in range(self.horizon)
        ], dtype=np.float32)

        # Action: start (0/1) for each appliance
        self.action_space = spaces.MultiBinary(self.n_appliances)
        # Observation: time_norm + remaining_norm + price_norm
        obs_low = np.zeros(1 + self.n_appliances + 1, dtype=np.float32)
        obs_high = np.ones(1 + self.n_appliances + 1, dtype=np.float32)
        self.observation_space = spaces.Box(obs_low, obs_high, dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.t = 0
        self.remaining = np.zeros(self.n_appliances, dtype=int)
        self.history = {"power": [], "price": [], "actions": []}
        return self._get_obs(), {}

    def _get_obs(self):
        time_norm = self.t / (self.horizon - 1)
        rem_norm = np.array([
            self.remaining[i] / self.appliances[self.names[i]]["duration"]
            for i in range(self.n_appliances)
        ], dtype=np.float32)
        price_norm = (self.price[self.t] - self.price.min()) / (self.price.max() - self.price.min())
        return np.concatenate(([time_norm], rem_norm, [price_norm])).astype(np.float32)

    def step(self, action):
        for i, a in enumerate(action):
            if a == 1 and self.remaining[i] == 0:
                self.remaining[i] = self.appliances[self.names[i]]["duration"]

        total_power = self.fridge_power
        for i in range(self.n_appliances):
            if self.remaining[i] > 0:
                total_power += self.appliances[self.names[i]]["power"]

        price_t = float(self.price[self.t])
        cost = total_power * price_t
        reward = -cost

        for i in range(self.n_appliances):
            if self.remaining[i] > 0:
                self.remaining[i] -= 1

        self.history["power"].append(total_power)
        self.history["price"].append(price_t)
        self.history["actions"].append(action.copy())

        self.t += 1
        terminated = self.t >= self.horizon
        truncated = False

        info = {"cost": cost, "power": total_power, "price": price_t}

        if terminated:
            # Return a dummy observation (zeros) of the right shape
            obs = np.zeros(self.observation_space.shape, dtype=np.float32)
        else:
            obs = self._get_obs()

        return obs, reward, terminated, truncated, info


    def render(self, mode="human"):
        print(f"t={self.t}, last power={self.history['power'][-1]}")

    def close(self):
        pass
