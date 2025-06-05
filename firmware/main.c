#include <Arduino.h>
#include "config.h"
#include "sensor.h"
#include "actuators.h"
#include "mqtt_client.h"

void setup() {
    Serial.begin(115200);
    sensor_init();
    actuators_init();
    mqtt_setup();
}

void loop() {
    mqtt_loop();

    float t = read_temperature();
    float h = read_humidity();
    mqtt_publish_readings(t, h);

    delay(10000);
}
