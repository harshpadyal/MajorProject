# compare_two_households.py
import os
import numpy as np
import matplotlib.pyplot as plt
import imageio
from stable_baselines3 import PPO
from energy_env import EnergyEnv

MODELS_DIR = "models"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Load trained model
model = PPO.load(os.path.join(MODELS_DIR, "ppo_energy"))

# Rule-based baseline
def rule_policy(env):
    t = env.t
    action = np.zeros(env.n_appliances, dtype=int)
    if t == 9:  # morning
        action[0] = 1; action[1] = 1
    if t == 18: # evening
        action[2] = 1
    return action

def run_baseline():
    env = EnergyEnv()
    obs, _ = env.reset()
    done, total_cost = False, 0
    while not done:
        action = rule_policy(env)
        obs, reward, terminated, truncated, info = env.step(action)
        total_cost += info["cost"]
        done = terminated or truncated
    return total_cost, env

def run_rl():
    env = EnergyEnv()
    obs, _ = env.reset()
    done, total_cost = False, 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        if isinstance(action, np.ndarray) and action.ndim > 1:
            action = action[0]
        obs, reward, terminated, truncated, info = env.step(action)
        total_cost += info["cost"]
        done = terminated or truncated
    return total_cost, env

# Run comparisons
baseline_costs = []
rl_costs = []
for _ in range(30):
    c, _ = run_baseline()
    baseline_costs.append(c)
    c, _ = run_rl()
    rl_costs.append(c)

print("Baseline mean cost:", np.mean(baseline_costs))
print("RL mean cost:", np.mean(rl_costs))

# Bar chart
plt.figure(figsize=(6,4))
plt.bar(["Baseline", "Agentic AI"], [np.mean(baseline_costs), np.mean(rl_costs)], 
        yerr=[np.std(baseline_costs), np.std(rl_costs)], capsize=5)
plt.ylabel("Daily cost (₹)")
plt.title("Household Cost Comparison")
plt.savefig(os.path.join(RESULTS_DIR, "cost_compare_bar.png"))
plt.close()
print("Saved cost_compare_bar.png")

# Example day timelines
c1, env_base = run_baseline()
c2, env_rl = run_rl()
plt.figure(figsize=(10,6))
plt.subplot(2,1,1)
plt.plot(env_base.history["power"], '-o', label="Power (kW)")
plt.title("Baseline Household")
plt.ylabel("Power (kW)")
plt.legend()
plt.subplot(2,1,2)
plt.plot(env_rl.history["power"], '-o', label="Power (kW)")
plt.title("Agentic AI Household")
plt.ylabel("Power (kW)")
plt.xlabel("Hour")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, "timeline_side_by_side.png"))
plt.close()
print("Saved timeline_side_by_side.png")

# Make side-by-side GIF
frames = []
for h in range(24):
    fig, axs = plt.subplots(1,2, figsize=(8,3))
    axs[0].bar(["power"], [env_base.history["power"][h]])
    axs[0].set_ylim(0, max(env_base.history["power"])*1.5)
    axs[0].set_title(f"Baseline hour {h}")
    axs[1].bar(["power"], [env_rl.history["power"][h]])
    axs[1].set_ylim(0, max(env_rl.history["power"])*1.5)
    axs[1].set_title(f"RL hour {h}")
    fname = f"_frame_{h}.png"
    fig.savefig(fname)
    plt.close(fig)
    frames.append(imageio.imread(fname))
imageio.mimsave(os.path.join(RESULTS_DIR, "side_by_side.gif"), frames, fps=2)
print("Saved side_by_side.gif")
