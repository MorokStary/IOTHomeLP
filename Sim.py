#!/usr/bin/env python3
# simulator.py

import time
import random
import paho.mqtt.client as mqtt

# перелік кімнат
ROOMS = ["kitchen", "bedroom1", "bedroom2"]
# інтервал між видачами даних (секунди)
PUBLISH_INTERVAL = 5.0

class HomeSimulator:
    def __init__(self,
                 broker_host="broker.hivemq.com",
                 broker_port=1883,
                 interval=PUBLISH_INTERVAL):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.interval = interval

        # ініціалізація стану: для кожної кімнати – температура, вологість, sprayer, heater
        self.state = {
            room: {
                "temperature": random.uniform(18.0, 24.0),
                "humidity":    random.uniform(40.0, 60.0),
                "sprayer": False,
                "heater":  False
            }
            for room in ROOMS
        }

        # створюємо MQTT-клієнта та призначаємо колбеки
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[INFO] Connected to {self.broker_host}:{self.broker_port}")
            # підписуємося на команди для кожної кімнати
            for room in ROOMS:
                client.subscribe(f"LPNU_HOME/{room}/sprayer")
                client.subscribe(f"LPNU_HOME/{room}/heater")
        else:
            print(f"[ERROR] MQTT connect failed (rc={rc})")

    def _on_message(self, client, userdata, msg):
        _, room, cmd = msg.topic.split("/")
        payload = msg.payload.decode().strip().upper()
        if room in self.state and cmd in ("sprayer", "heater"):
            self.state[room][cmd] = (payload == "ON")
            print(f"[CMD] {room} {cmd} → {payload}")

    def _update_environment(self):
        for room, vals in self.state.items():
            # випадковий дрейф температури та вологості
            vals["temperature"] += random.uniform(-0.1, 0.1)
            vals["humidity"]    += random.uniform(-1.0, 1.0)

            # ефект sprayer: +2% вологості за цикл
            if vals["sprayer"]:
                vals["humidity"] += 2.0
            # ефект heater: +0.5°C за цикл
            if vals["heater"]:
                vals["temperature"] += 0.5

            # обмеження значень у реалістичних межах
            vals["temperature"] = max(0.0, min(50.0, vals["temperature"]))
            vals["humidity"]    = max(0.0, min(100.0, vals["humidity"]))

    def start(self):
        self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        self.client.loop_start()

        try:
            while True:
                self._update_environment()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                for room, vals in self.state.items():
                    t = f"{vals['temperature']:.1f}"
                    h = f"{vals['humidity']:.1f}"
                    self.client.publish(f"LPNU_HOME/{room}/temperature", t)
                    self.client.publish(f"LPNU_HOME/{room}/humidity", h)
                    print(f"[PUB] {timestamp} | {room} → T={t}°C  H={h}%")
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n[INFO] Simulator stopped by user")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    sim = HomeSimulator()
    sim.start()
