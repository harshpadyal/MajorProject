from envs.household_simulation import HouseholdSimulation
import time

env = HouseholdSimulation()

# Number of simulation steps
total_steps = 200

for t in range(total_steps):
    # Example random control actions
    action = {
        "ac": t % 40 < 10,             # AC on for 10 steps every 40
        "heater": False,               # heater off
        "fan_speed": (t // 50) % 4,    # cycles through 0–3 speeds
        "bulb": t % 2 == 0             # bulb toggles each step
    }

    state, reward, done, _ = env.step(action)
    env.render()
    time.sleep(0.05)

    if done:
        break

print("Simulation finished!")
