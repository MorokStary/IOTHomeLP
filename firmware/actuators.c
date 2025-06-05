#include <Arduino.h>
#include "config.h"
#include "actuators.h"

void actuators_init() {
    pinMode(SPRAYER_PIN, OUTPUT);
    pinMode(HEATER_PIN, OUTPUT);
    digitalWrite(SPRAYER_PIN, HIGH);
    digitalWrite(HEATER_PIN, HIGH);
}

void set_sprayer(bool on) {
    digitalWrite(SPRAYER_PIN, on ? LOW : HIGH);
}

void set_heater(bool on) {
    digitalWrite(HEATER_PIN, on ? LOW : HIGH);
}
