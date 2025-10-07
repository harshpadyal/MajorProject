# train_and_eval.py
import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import check_env
from energy_env import EnergyEnv

MODELS_DIR = "models"
RESULTS_DIR = "results"
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Train PPO agent
env = DummyVecEnv([lambda: EnergyEnv()])
check_env(EnergyEnv(), warn=True)

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)
model.save(os.path.join(MODELS_DIR, "ppo_energy"))

# Evaluate RL agent
def run_rl_episode():
    e = EnergyEnv()
    obs, _ = e.reset()
    done = False
    total_cost = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        if isinstance(action, np.ndarray) and action.ndim > 1:
            action = action[0]
        obs, reward, terminated, truncated, info = e.step(action)
        total_cost += info["cost"]
        done = terminated or truncated
    return total_cost, e

cost, env = run_rl_episode()
print("Example daily cost with RL agent:", cost)

# Plot timeline
t = range(24)
plt.figure(figsize=(8,4))
plt.plot(t, env.history["power"], '-o', label="Power (kW)")
plt.plot(t, env.history["price"], '-s', label="Price (₹/kWh)")
plt.legend()
plt.xlabel("Hour")
plt.title("RL Agent: Power vs Price")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "timeline.png"))
print("Saved timeline.png")
