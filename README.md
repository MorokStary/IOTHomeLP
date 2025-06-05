# IoT Home Lab Platform

This project demonstrates a simple home climate monitoring and control system built around MQTT. The repository contains:

* `firmware/` – ESP32 firmware split into modules for sensors, actuators and MQTT;
* `Sim.py` – a Python simulator that mimics the behaviour of multiple rooms and publishes MQTT data;
* `dashboard.py` and `mqtt_handler.py` – a Streamlit dashboard used to visualise sensor data and send control commands;
* `UML/` – PlantUML diagrams of the system.

## Hardware

The firmware for the ESP32 lives in the `firmware/` directory and uses the
`PubSubClient` MQTT library. It is organised into several small modules:

* `config.h` – configuration for Wi‑Fi, MQTT and pin assignments;
* `sensor.[ch]` – DHT22 driver;
* `actuators.[ch]` – sprayer and heater control;
* `mqtt_client.[ch]` – Wi‑Fi/MQTT connection logic;
* `main.c` – application entry point.

Open the directory with the Arduino IDE or `platformio`, adjust `config.h` with
your network credentials and flash the firmware to the ESP32.

The device publishes sensor readings to topics of the form:

```
LPNU_HOME/<room>/temperature
LPNU_HOME/<room>/humidity
```

It listens for control messages on:

```
LPNU_HOME/<room>/sprayer
LPNU_HOME/<room>/heater
```

Payloads `ON` or `OFF` will toggle the relevant pin.

## Dashboard

The dashboard relies on a running MQTT broker (default `broker.hivemq.com`) and displays real‑time values. Run it with:

```bash
streamlit run dashboard.py
```

A simple simulator is also available and can be started with:

```bash
python Sim.py
```

## Installation

Install Python dependencies using:

```bash
pip install -r requirements.txt
```

Then launch the Streamlit dashboard as shown above. If you are using real hardware,
build the sources in `firmware/` and upload the resulting binary to your ESP32.
