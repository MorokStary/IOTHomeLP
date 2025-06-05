import paho.mqtt.client as mqtt
from datetime import datetime

# перелік кімнат
ROOMS = ["kitchen", "bedroom1", "bedroom2"]

# спільний стан для Streamlit
sensor_data = {
    room: {
        "temperature": None,
        "humidity":    None,
        "sprayer":     None,
        "heater":      None
    }
    for room in ROOMS
}
sensor_data["timestamp"] = None

class HomeMQTTClient:
    """
    MQTT-обробник для домашньої IoT-платформи.
    Підписується на сенсорні та командні теми, оновлює `sensor_data`
    і дозволяє відправляти команди керування.
    """

    def __init__(self,
                 broker_host: str = "broker.hivemq.com",
                 broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()

        # список тем для підписки: для кожної кімнати – сенсори й виконавчі пристрої
        self.topics = [
            f"LPNU_HOME/{room}/{metric}"
            for room in ROOMS
            for metric in ("temperature", "humidity", "sprayer", "heater")
        ]

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[INFO] Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            for topic in self.topics:
                client.subscribe(topic)
                print(f"[INFO] Subscribed to {topic}")
        else:
            print(f"[ERROR] Connection failed (rc={rc})")

    def _on_message(self, client, userdata, msg):
        payload   = msg.payload.decode().strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _, room, metric = msg.topic.split("/")  # e.g. ["home", "kitchen", "temperature"]

        if room in sensor_data and metric in sensor_data[room]:
            sensor_data[room][metric] = payload
            sensor_data["timestamp"] = timestamp
            print(f"[DATA] {timestamp} | {room}.{metric} = {payload}")

    def start(self):
        """
        Підключається до брокера і запускає MQTT-цикл у фоні.
        """
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            print("[INFO] MQTT loop started")
        except Exception as e:
            print(f"[ERROR] MQTT start failed: {e}")

    def publish_command(self, room: str, metric: str, message: str):
        """
        Надсилає команду керування (ON/OFF) для заданої кімнати й виконавчого пристрою.
        :param room: назва кімнати, наприклад "kitchen"
        :param metric: "sprayer" або "heater"
        :param message: "ON" або "OFF"
        """
        if room in ROOMS and metric in ("sprayer", "heater"):
            topic = f"LPNU_HOME/{room}/{metric}"
            self.client.publish(topic, message)
            print(f"[CMD] Published {message} → {topic}")
        else:
            print(f"[WARN] Invalid command target: {room}.{metric}")
