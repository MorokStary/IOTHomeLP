#include <WiFi.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
#include "DHT.h"


#define ROOM_NAME       "kitchen"

#define TOPIC_ROOT      "LPNU_HOME"

#define TOPIC_TEMPERATURE  TOPIC_ROOT "/" ROOM_NAME "/temperature"
#define TOPIC_HUMIDITY     TOPIC_ROOT "/" ROOM_NAME "/humidity"
#define TOPIC_SPRAYER      TOPIC_ROOT "/" ROOM_NAME "/sprayer"
#define TOPIC_HEATER       TOPIC_ROOT "/" ROOM_NAME "/heater"


#define WLAN_SSID       "TELL_Net"
#define WLAN_PASS       "123AAAdff"


#define AIO_SERVER      "broker.hivemq.com"
#define AIO_SERVERPORT  1883


#define DHTPIN          4
#define DHTTYPE         DHT22
DHT dht(DHTPIN, DHTTYPE);


const int SprayerPin = 25;
const int HeaterPin  = 26;


WiFiClient      wifiClient;
Adafruit_MQTT_Client mqtt(&wifiClient, AIO_SERVER, AIO_SERVERPORT);


Adafruit_MQTT_Publish pubTemp    = Adafruit_MQTT_Publish(&mqtt, TOPIC_TEMPERATURE);
Adafruit_MQTT_Publish pubHum     = Adafruit_MQTT_Publish(&mqtt, TOPIC_HUMIDITY);





Adafruit_MQTT_Subscribe subSprayer = Adafruit_MQTT_Subscribe(&mqtt, TOPIC_SPRAYER);
Adafruit_MQTT_Subscribe subHeater  = Adafruit_MQTT_Subscribe(&mqtt, TOPIC_HEATER);


void connectWiFi() {
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(500);
}

void MQTT_connect() {
  if (mqtt.connected()) return;
  uint8_t retries = 3;
  while (mqtt.connect() != 0) {
    mqtt.disconnect();
    delay(5000);
    if (--retries == 0) while (1);
  }
}

void setup() {
  pinMode(SprayerPin, OUTPUT);
  pinMode(HeaterPin, OUTPUT);
  digitalWrite(SprayerPin, HIGH);
  digitalWrite(HeaterPin, HIGH);

  Serial.begin(115200);
  dht.begin();

  connectWiFi();
  mqtt.subscribe(&subSprayer);
  mqtt.subscribe(&subHeater);
}

void loop() {
  MQTT_connect();

  
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (!isnan(t)) pubTemp.publish(t);
  if (!isnan(h)) pubHum.publish(h);

  
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(5000))) {
    if (subscription == &subSprayer) {
      bool on = (strcmp((char*)subSprayer.lastread, "ON") == 0);
      digitalWrite(SprayerPin, on ? LOW : HIGH);
    }
    if (subscription == &subHeater) {
      bool on = (strcmp((char*)subHeater.lastread, "ON") == 0);
      digitalWrite(HeaterPin, on ? LOW : HIGH);
    }
  }

  delay(10000);  
}
