# Inkbird to Homeassistant
## The purpose of this project is to get popular multi-probe inkbird thermometers into homeassistant for automations, temperature logging, and general awesomeness.

## Requirements

This is designed to run on a raspberry pi, but it should work fine on any linux system with a BLE adapter. It should even run on a raspberry pi zero w.


## Quick Start
The easiest way to run this probject is to run the image from docker hub using docker-compose

wget https://raw.githubusercontent.com/jshridha/inkbird/master/docker-compose.yaml

You will need to modify the environmental variables
* `INKBIRD_MQTT_HOST` is the MQTT server that home assistant uses
* `INKBIRD_ADDRESS` is the bluetooth address for the inkbird

Then just run `docker-compose up -d`
