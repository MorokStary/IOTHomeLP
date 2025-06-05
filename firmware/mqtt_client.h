#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

void mqtt_setup();
void mqtt_loop();
void mqtt_publish_readings(float temperature, float humidity);

#endif // MQTT_CLIENT_H
