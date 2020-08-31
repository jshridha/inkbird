import os
import json
from .mqtt import client as mqtt

import logging
from inkbird.version import version

logger = logging.getLogger("inkbird")


class Sensor:
    def __init__(self, mac):
        self.mac = mac.lower().replace(":", "").replace("_", "")
        self.set_logger()
        self.discover()

    def discover(self):
        mqtt.publish(self.discovery_topic(), json.dumps(self.discovery_message))

    def update(self):
        mqtt.publish(self.publish_topic(), self.message)
        self.logger.info(f"Updating state with {self.message}")

    def set_logger(self):
        self.logger = logger

    def build_message(self):
        return {}

    @property
    def message(self):
        return json.dumps(self.build_message())

    @property
    def discovery_message(self):
        return {
            "unit_of_measurement": self.units().upper(),
            "device_class": self.device_class(),
            "value_template": self.value_template(),
            "state_topic": self.publish_topic(),
            "json_attributes_topic": self.publish_topic(),
            "name": self.name(),
            "unique_id": self.unique_id(),
            "device": {
                "identifiers": [f"inkbird_{self.mac.replace(':', '')}"],
                "name": f"Inkbird BBQ Thermometer",
                "sw_version": version,
                "model": "Inkbird Smart BBQ Thermometer",
                "manufacturer": "Inkbird",
            },
            "availability_topic": "inkbird/status",
        }

    def name(self):
        return "Inkbird iBBQ"

    def unique_id(self):
        return f"inkbird_{self.mac}"

    def value_template(self):
        return ""

    def publish_topic(self):
        return f"inkbird/{self.mac}"

    def discovery_topic(self):
        return f"homeassistant/sensor/{self.mac}"


class Probe(Sensor):
    def __init__(self, mac, probe, battery=None):
        self.probe = probe
        self._temperature = "not_set"
        self._battery = battery
        self._units = os.environ.get("INKBIRD_TEMP_UNITS", "f").lower()

        super().__init__(mac)

    def build_message(self):
        return {"temperature": self.temperature, "battery": self.battery}

    def discovery_topic(self):
        return f"{super().discovery_topic()}/Probe{self.probe}/config"

    def publish_topic(self):
        return f"{super().publish_topic()}/Probe{self.probe}"

    def name(self):
        return f"{super().name()} Probe {self.probe}"

    def unique_id(self):
        return f"{super().unique_id()}_probe{self.probe}"

    def device_class(self):
        return "temperature"

    def units(self):
        return self._units

    def value_template(self):
        return "{{ value_json.temperature }}"

    def set_logger(self):
        self.logger = logger.getChild(f"Probe{self.probe}")

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
        if self.units() == "c":
            temperature = temperature / 10 if temperature > 0 else None
        else:
            temperature = temperature / 10 * 9 / 5 + 32 if temperature > 0 else None
        if self._temperature == temperature:
            return
        self._temperature = temperature
        self.update()


class Battery(Sensor):
    def __init__(self, mac):
        self._value = None
        super().__init__(mac)

    def build_message(self):
        return {"value": self.value}

    def discovery_topic(self):
        return f"{super().discovery_topic()}/battery/config"

    def publish_topic(self):
        return f"{super().publish_topic()}/battery"

    def name(self):
        return f"{super().name()} Battery"

    def unique_id(self):
        return f"{super().unique_id()}_battery"

    def value_template(self):
        return "{{ value_json.value }}"

    def set_logger(self):
        self.logger = logger.getChild("battery")

    def device_class(self):
        return "battery"

    def units(self):
        return "%"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self._value = value
        self.update()
