#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino.h>
#include "config.h"
#include "actuators.h"
#include "mqtt_client.h"

static WiFiClient espClient;
static PubSubClient client(espClient);

static void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (unsigned int i = 0; i < length; ++i) {
        msg += (char)payload[i];
    }
    if (strcmp(topic, TOPIC_SPRAYER) == 0) {
        set_sprayer(msg == "ON");
    } else if (strcmp(topic, TOPIC_HEATER) == 0) {
        set_heater(msg == "ON");
    }
}

static void connect_wifi() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
}

static void connect_mqtt() {
    while (!client.connected()) {
        if (client.connect("esp32")) {
            client.subscribe(TOPIC_SPRAYER);
            client.subscribe(TOPIC_HEATER);
        } else {
            delay(5000);
        }
    }
}

void mqtt_setup() {
    connect_wifi();
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqtt_callback);
}

void mqtt_loop() {
    if (!client.connected()) {
        connect_mqtt();
    }
    client.loop();
}

void mqtt_publish_readings(float temperature, float humidity) {
    if (!isnan(temperature)) {
        client.publish(TOPIC_TEMPERATURE, String(temperature).c_str());
    }
    if (!isnan(humidity)) {
        client.publish(TOPIC_HUMIDITY, String(humidity).c_str());
    }
}
