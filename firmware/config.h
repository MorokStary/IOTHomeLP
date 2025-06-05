#ifndef CONFIG_H
#define CONFIG_H

#define ROOM_NAME "kitchen"
#define TOPIC_ROOT "LPNU_HOME"

#define TOPIC_TEMPERATURE TOPIC_ROOT "/" ROOM_NAME "/temperature"
#define TOPIC_HUMIDITY    TOPIC_ROOT "/" ROOM_NAME "/humidity"
#define TOPIC_SPRAYER     TOPIC_ROOT "/" ROOM_NAME "/sprayer"
#define TOPIC_HEATER      TOPIC_ROOT "/" ROOM_NAME "/heater"

#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASS "YOUR_PASSWORD"

#define MQTT_SERVER "broker.hivemq.com"
#define MQTT_PORT   1883

#define DHTPIN   4
#define DHTTYPE  DHT22

#define SPRAYER_PIN 25
#define HEATER_PIN  26

#endif // CONFIG_H
