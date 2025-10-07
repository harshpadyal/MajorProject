from envs.household_simulation_gui import HouseholdSimulationGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = HouseholdSimulationGUI(root)
    root.mainloop()
