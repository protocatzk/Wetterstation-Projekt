"""
Messstation für verschiedene Schadstoffe.
"""
__author__ = "Soeren Leutheuser"

import random
import datetime
import time
import json
import threading
import logging
import tkinter as tk
from tkinter import ttk

class MobileMessstation:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger()

    def __init__(self, station_id):
        self.station_id = station_id
        self.sensors = {
            "NO2": 0,
            "PM10": 0,
            "O3": 0,
            "CO": 0,
            "SO": 0,
            "Temp": 0
        }



    def parametrisieren(self, params):
        for sensor, value in params.items():
            if sensor in self.sensors:
                self.sensors[sensor] = value

    def messen(self):
        timestamp = datetime.datetime.now()

        data = {
            "station_id": self.station_id,
            "timestamp": timestamp.strftime('%H:%M:%S'),
            "data": {sensor: round(random.uniform(max(0, value), value + 5), 2) if sensor != "Temp" else round(value, 2) for sensor, value in self.sensors.items()}
        }
        return data

    def luftqualitaet_bewerten(self, sensor, value):
        if sensor == "NO2":
            return self.bewerte_luftqualitaet(value, [50, 100, 150, 200, 400, 1000])
        elif sensor == "PM10":
            return self.bewerte_luftqualitaet(value, [10, 20, 25, 50, 75, 100])
        elif sensor == "O3":
            return self.bewerte_luftqualitaet(value, [30, 70, 100, 150, 200, 300])
        elif sensor == "CO":
            return self.bewerte_luftqualitaet(value, [1, 2, 5, 10, 20, 40])
        elif sensor == "SO":
            return self.bewerte_luftqualitaet(value, [0.1, 0.2, 0.5, 1.1, 1.2, 2])
        else:
            return "N/A"

    def bewerte_luftqualitaet(self, value, klassen):
        for i in range(len(klassen) - 1, -1, -1):
            if value >= klassen[i]:
                return f"Stufe {i + 1}"
        return "N/A"

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mobile Umwelt-Messstationen")
        self.geometry("1600x400")

        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = ("station_id", "timestamp", "NO2", "LQ(NO2)", "PM10", "LQ(PM10)", "O3", "LQ(O3)", "CO", "LQ(CO)", "SO",  "LQ(SO)", "Temp")

        for column in self.tree["columns"]:
            self.tree.column(column, anchor="nw", width=100)
            self.tree.heading(column, text=column, anchor="nw")

        # Luftgüteklassen definieren
        for i in range(1, 7):
            self.tree.tag_configure(f"Stufe {i}", background=self.get_color_for_class(i), foreground="black")

        self.tree.pack(pady=20)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=scrollbar.set)

        start_button = ttk.Button(self, text="Start", command=self.start_simulation)
        start_button.pack()

        stop_button = ttk.Button(self, text="Stop", command=self.stop_simulation)
        stop_button.pack()

        self.is_running = False
        self.simulation_thread = None

    def get_color_for_class(self, class_number):
        # Funktion zur Auswahl von Farben je nach Luftgüteklasse
        # Hier kannst du eigene Farbzuweisungen hinzufügen
        colors = ["lightgreen", "green", "yellow", "orange", "red", "purple"]
        return colors[class_number - 1] if 1 <= class_number <= len(colors) else "white"

    def start_simulation(self):
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(target=self.simulation)
            self.simulation_thread.start()

    def stop_simulation(self):
        self.is_running = False

    def simulation(self):
        num_stations = 2
        stations = [MobileMessstation(station_id=i) for i in range(1, num_stations + 1)]

        while self.is_running:
            for station in stations:
                params = {
                    "NO2": random.randint(1, 500),
                    "PM10": random.randint(1, 100),
                    "O3": random.randint(1, 241),
                    "CO": random.uniform(0.1, 30),
                    "SO": random.uniform(0.1, 3.0),
                    "Temp": random.uniform(-10, 40)
                }
                station.parametrisieren(params)
                data = station.messen()
                self.update_tree(data)
                self.tree.yview_moveto(1)  # Scrollt zum Ende der Liste
                time.sleep(1)  # Simuliere einen Intervall von 1 Sekunde zwischen den Messungend

    def update_tree(self, data):
        luftqualitaet_no2 = MobileMessstation(data["station_id"]).luftqualitaet_bewerten("NO2", data["data"]["NO2"])
        luftqualitaet_pm10 = MobileMessstation(data["station_id"]).luftqualitaet_bewerten("PM10", data["data"]["PM10"])
        luftqualitaet_o3 = MobileMessstation(data["station_id"]).luftqualitaet_bewerten("O3", data["data"]["O3"])
        luftqualitaet_co = MobileMessstation(data["station_id"]).luftqualitaet_bewerten("CO", data["data"]["CO"])
        luftqualitaet_so = MobileMessstation(data["station_id"]).luftqualitaet_bewerten("SO", data["data"]["SO"])

        values = (
            data["station_id"],
            data["timestamp"],
            data["data"]["NO2"],
            luftqualitaet_no2,
            data["data"]["PM10"],
            luftqualitaet_pm10,
            data["data"]["O3"],
            luftqualitaet_o3,
            max(0, data["data"]["CO"]),  # Stelle sicher, dass CO nicht negativ ist
            luftqualitaet_co,
            max(0, data["data"]["SO"]),  # Stelle sicher, dass SO nicht negativ ist
            luftqualitaet_so,
            round(data["data"]["Temp"], 2),  # Runde Temperatur auf 2 Dezimalstellen
        )
        self.tree.insert("", "end", values=values, tags=(luftqualitaet_no2, luftqualitaet_pm10, luftqualitaet_o3, luftqualitaet_co, luftqualitaet_so))

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
