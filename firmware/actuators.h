#ifndef ACTUATORS_H
#define ACTUATORS_H

#include <stdbool.h>

void actuators_init();
void set_sprayer(bool on);
void set_heater(bool on);

#endif // ACTUATORS_H
