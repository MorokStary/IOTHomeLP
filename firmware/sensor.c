#include <Arduino.h>
#include <DHT.h>
#include "config.h"
#include "sensor.h"

static DHT dht(DHTPIN, DHTTYPE);

void sensor_init() {
    dht.begin();
}

float read_temperature() {
    return dht.readTemperature();
}

float read_humidity() {
    return dht.readHumidity();
}
