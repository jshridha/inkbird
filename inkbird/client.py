import os
import asyncio
import array
from collections import deque
import struct
import logging
import threading


from .hass import Probe, Battery

from bluepy import btle

from . import const
from collections import defaultdict

logger = logging.getLogger("inkbird")

class Timer(threading.Timer):
    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()
 
class key_dependent_dict(defaultdict):
    def __init__(self,f_of_x):
        super().__init__(None) # base class doesn't get a factory
        self.f_of_x = f_of_x # save f(x)
    def __missing__(self, key): # called when a default needed
        ret = self.f_of_x(key) # calculate default value
        self[key] = ret # and install it in the dict
        return ret

class Delegate(btle.DefaultDelegate):
    def __init__(self, address):
        super().__init__()
        self.address = address
        self.probes = key_dependent_dict(lambda x: Probe(self.address, x))
        self._battery = None

    def handleNotification(self, cHandle, data):
        logger.debug(f"New Data: {(cHandle, data)}")
        if cHandle == 48:
            self.handleTemperature(data)
        if cHandle == 37:
            self.handleBattery(data)
    
    def handleTemperature(self, data):
        temp = array.array("H")
        temp.fromstring(data)
        for probe, t in enumerate(temp):
            self.probes[probe + 1].temperature = t
    
    def handleBattery(self, data):
        if data[0] != 36:
            return
        battery, maxBattery = struct.unpack("<HH", data[1:5])
        battery = int(battery/maxBattery*100)
        for probe, sensor in self.probes.items():
            sensor.battery = battery
        self.battery.value = battery

    @property
    def battery(self):
        if self._battery is None:
            self._battery = Battery(self.address)
        return self._battery

class InkBirdClient:
    def __init__(self, address):
        self.address = address
        self.units = os.environ.get("INKBIRD_TEMP_UNITS", "f").lower()

    def connect(self):
        self.client = btle.Peripheral(self.address)
        self.service = self.client.getServiceByUUID("FFF0")
        self.characteristics = self.service.getCharacteristics()
        self.client.setDelegate(Delegate(self.address))
        self.client.writeCharacteristic(self.characteristics[0].getHandle() + 1, b"\x01\x00", withResponse=True)
        self.client.writeCharacteristic(self.characteristics[3].getHandle() + 1, b"\x01\x00", withResponse=True)
        if self.units == "c":
            self.set_deg_c()
        else:
            self.set_deg_f()

    def login(self):
        self.characteristics[1].write(const.CREDENTIALS_MESSAGE, withResponse=True)

    def enable_data(self):
        self.characteristics[4].write(const.REALTIME_DATA_ENABLE_MESSAGE, withResponse=True)

    def enable_battery(self):
        timer = Timer(300.0, self.request_battery)
        timer.start()

    def request_battery(self):
        logger.debug("Requesting battery")
        try:
            self.characteristics[4].write(const.REQ_BATTERY_MESSAGE, withResponse=True)
        except (btle.BTLEInternalError, btle.BTLEDisconnectError):
            pass

    def set_deg_f(self):
        self.characteristics[4].write(const.UNITS_F_MESSAGE, withResponse=True)

    def set_deg_c(self):
        self.characteristics[4].write(const.UNITS_C_MESSAGE, withResponse=True)

    def read_temperature(self):
        return self.service.peripheral.readCharacteristic(self.characteristics[3].handle)
