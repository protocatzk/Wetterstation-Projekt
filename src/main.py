import logging
import tkinter as tk
from tkinter import ttk
import json
import random


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wettermessstation")

        # Logger
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
        self.log = logging.getLogger('WMS')

        # Lese Konfigurationsdatei
        try:
            with open('config.json', 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError as e:
            self.log.error(f'Fehler beim Öffnen der Datei: {e}')
            exit(1)

        # Simulierte Werte initialisieren
        self.sensor_values = {sensor['type']: self.generate_sensor_value(sensor['type']) for sensor in self.config}

        # GUI-Elemente erstellen
        self.create_widgets()

    def create_widgets(self):
        # Sensoren aktivieren/deaktivieren
        toggle_frame = ttk.LabelFrame(self.root, text="Sensoren aktivieren/deaktivieren")
        toggle_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        for sensor in self.config:
            sensor_var = tk.BooleanVar(value=sensor['active'])
            sensor_checkbox = ttk.Checkbutton(toggle_frame, text=sensor['type'], variable=sensor_var,
                                              command=lambda s=sensor['type'], v=sensor_var: self.toggle_sensor(s, v))
            sensor_checkbox.pack(side=tk.TOP, padx=10, pady=5)

        # Anweisungen
        instruction_frame = ttk.LabelFrame(self.root, text="Anweisungen für Sensoren")
        instruction_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        instruction_label = ttk.Label(instruction_frame, text="Grenzwerte für Bewertung der Luftqualität:")
        instruction_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        for sensor in self.config:
            threshold_label = ttk.Label(instruction_frame, text=f"{sensor['type']}: {sensor['threshold']}")
            threshold_label.grid(row=self.config.index(sensor) + 1, column=0, padx=10, pady=5, sticky="w")

        # Simulierte Sensordaten und Bewertung
        data_frame = ttk.LabelFrame(self.root, text="Sensordaten und Bewertung")
        data_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        self.data_label = ttk.Label(data_frame, text="")
        self.data_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Schließe die GUI an die Aktualisierung der Daten an
        self.root.after(1750, self.update_values)

    def update_values(self):
        # Aktualisiere die simulierten Werte der Sensoren
        data_str = ""
        for sensor_type, value in self.sensor_values.items():
            if self.is_sensor_active(sensor_type):
                data_str += f"{sensor_type}: {value:.2f} - Stufe: {self.get_threshold_level(sensor_type)}  \n"
                # Zufällige Aktualisierung des Werts
                self.sensor_values[sensor_type] = self.generate_sensor_value(sensor_type)

        # Aktualisiere das Label mit den Sensordaten
        self.data_label.config(text=data_str)

        # Nach einer Sekunde erneut aktualisieren
        self.root.after(1000, self.update_values)

    def is_sensor_active(self, sensor_type):
        # Überprüfe, ob der Sensor aktiv ist
        for sensor in self.config:
            if sensor['type'] == sensor_type:
                return sensor['active']
        return False

    def toggle_sensor(self, sensor_type, var):
        # Schalte den ausgewählten Sensor ein/aus
        for sensor in self.config:
            if sensor['type'] == sensor_type:
                sensor['active'] = var.get()
                self.log.debug(f'Änderung Sensor {sensor['type']}: {sensor['active']}')

    def get_threshold_level(self, sensor_type):
        # Bestimme die Stufe für die Bewertung des Sensorwerts
        value = self.sensor_values[sensor_type]
        thresholds = [float(t) for t in
                      next(sensor['threshold'] for sensor in self.config if sensor['type'] == sensor_type)]

        for i, threshold in enumerate(thresholds, start=1):
            if value <= threshold:
                return i
        return len(thresholds) + 1  # Wert außerhalb des definierten Bereichs

    def generate_sensor_value(self, sensor_type):
        # Generiere einen zufälligen Wert im Bereich der Schwellenwerte
        thresholds = [float(t) for t in
                      next(sensor['threshold'] for sensor in self.config if sensor['type'] == sensor_type)]
        return random.triangular(min(thresholds), max(thresholds))


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
