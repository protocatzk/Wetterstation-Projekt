"""
Wettermessstation

@author sl91mano
"""

import time
import tkinter as tk
from tkinter import ttk
import json
import random


class WeatherApp:
    def __init__(self, root, config_file):
        self.root = root
        self.root.title("Wettermessstation")

        self.config_data = self.load_config(config_file)
        self.sensor_values = {sensor["type"]: random.uniform(-20, 45) for sensor in self.config_data}

        self.label_vars = {}

        self.create_gui()
        self.start_auto_update()

    def load_config(self, config_file):
        try:
            with open(config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Die Konfigurationsdatei '{config_file}' wurde nicht gefunden.")
            return []

    def create_gui(self):
        for i, sensor in enumerate(self.config_data):
            if sensor["active"]:
                frame = ttk.Frame(self.root, padding="10")
                frame.grid(row=i // 3, column=i % 3, sticky="nsew", padx=10, pady=10)

                ttk.Label(frame, text=sensor["type"]).grid(row=0, column=0, columnspan=3)

                # Create TreeView for values
                value_tree = ttk.Treeview(frame, columns=("Time", "Value", "Status"))
                value_tree.heading("Time", text="Zeit")
                value_tree.heading("Value", text="Wert")
                value_tree.heading("Status", text="Status")

                # Set column widths
                value_tree.column("#0", width=0)
                value_tree.column("Time", width=120)
                value_tree.column("Value", width=80)
                value_tree.column("Status", width=80)

                value_tree.grid(row=1, column=0, columnspan=3)

                # Speichern der Instanzvariablen für jedes TreeView
                self.label_vars[sensor["type"]] = {"value_tree": value_tree}

    def get_status(self, sensor_type):
        value = self.sensor_values[sensor_type]
        thresholds = next(d["threshold"] for d in self.config_data if d["type"] == sensor_type)

        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return f"Stufe {i + 1}"
        return f"Stufe {len(thresholds) + 1}"

    def update_value(self, sensor_type, value_tree):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        value = round(random.uniform(-20, 45), 2)
        status = self.get_status(sensor_type)

        # Insert new values into the TreeView
        value_tree.column("Time", width=120)  # Set a fixed width for the "Time" column
        value_tree.insert("", "end", values=(timestamp, value, status))

    def auto_update(self):
        for sensor_type in self.sensor_values:
            self.update_value(sensor_type, self.label_vars[sensor_type]["value_tree"])

        self.root.after(5000, self.auto_update)

    def start_auto_update(self):
        self.root.after(0, self.auto_update)


if __name__ == "__main__":
    config_file_path = "config.json"

    root = tk.Tk()
    app = WeatherApp(root, config_file_path)
    root.mainloop()
