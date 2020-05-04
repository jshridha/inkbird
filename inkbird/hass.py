import json
from .mqtt import client as mqtt

import logging

logger = logging.getLogger("inkbird")


class Sensor:
    def __init__(self, mac, probe):
        self.mac = mac.lower().replace(':', '').replace("_", "")
        self.probe = probe
        self._temperature = "not_set"
        self._battery = None
        self.logger = logger.getChild(f"Probe{probe}")
        self.discover()

    def discover(self):
        mqtt.publish(self.discovery_topic, json.dumps(self.discovery_message))

    def update(self):
        message = {"battery": self.battery, "temperature": self.temperature}
        message = json.dumps(message)
        mqtt.publish(self.publish_topic, message)
        self.logger.info(f"Updating state with {message}")

    @property
    def discovery_message(self):
        return {
            "unit_of_measurement": "F",
            "device_class": "temperature",
            "value_template": "{{ value_json.temperature }}",
            "state_topic": self.publish_topic,
            "json_attributes_topic": self.publish_topic,
            "name": f"Inkbird iBBQ Probe{self.probe}",
            "unique_id": f"{self.mac}_{self.probe}",
            "device": {
                "identifiers": [f"inkbird_{self.mac.replace(':', '')}"],
                "name": f"Inkbird BBQ Thermometer",
                "sw_version": "0.1.0",
                "model": "Inkbird Smart BBQ Thermometer",
                "manufacturer": "Inkbird",
            },
            "availability_topic": "inkbird/status",
        }
    
    @property
    def publish_topic(self):
        return f"inkbird/{self.mac}/{self.probe}"

    @property
    def discovery_topic(self):
        return f"homeassistant/sensor/{self.mac}/{self.probe}/config"

    @property
    def temperature(self):
        return self._temperature

    @property
    def battery(self):
        return self._battery

    @battery.setter
    def battery(self, battery):
        if self._battery == battery:
            return
        self._battery = battery
        self.update()

    @temperature.setter
    def temperature(self, temperature):
        temperature = temperature/10 * 9/5 + 32 if temperature > 0 else None
        if self._temperature == temperature:
            return
        self._temperature = temperature
        self.update()
