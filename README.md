# Inkbird to Homeassistant
## The purpose of this project is to get popular multi-probe inkbird thermometers into homeassistant for automations, temperature logging, changing lights based on BBQ status, and whatever else you can think of.

## Requirements

This is designed to run on a raspberry pi, but it should work fine on any linux system with a BLE adapter.


## Quick Start
The easiest way to run this probject is to run the image from docker hub using docker-compose

wget https://raw.githubusercontent.com/jshridha/inkbird/master/docker-compose.yaml

You will need to modify the environmental variables
| Variable | Required (Y/N) | Description |
|----------|----------------|-------------|
| `INKBIRD_MQTT_HOST` | Y | MQTT server that home assistant uses
| `INKBIRD_ADDRESS` | Y | The bluetooth address for the inkbird
| `INKBIRD_MQTT_USERNAME` | N | MQTT username
| `INKBIRD_MQTT_PASSWORD` | N | MQTT password
| `INKBIRD_TEMP_UNITS` | N | Set to `F` for farenheit and `C` for celsius (defaults to `F`)

Then just run `docker-compose up -d`
