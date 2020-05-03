import asyncio
import array
from collections import deque
import struct
import logging


from .hass import Sensor

from bluepy import btle

from . import const
from collections import defaultdict

logger = logging.getLogger("inkbird")
 
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
        self.sensors = key_dependent_dict(lambda x: Sensor(self.address, x))

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
            self.sensors[probe].temperature = t
    
    def handleBattery(self, data):
        if data[0] != 36:
            return
        battery, maxBattery = struct.unpack("<HH", data[1:5])
        battery = int(battery/maxBattery*100)
        for probe, sensor in self.sensors.items():
            sensor.battery = battery

class InkBirdClient:
    def __init__(self, address):
        self.address = address

    def connect(self):
        self.client = btle.Peripheral(self.address)
        self.service = self.client.getServiceByUUID("FFF0")
        self.characteristics = self.service.getCharacteristics()
        self.client.setDelegate(Delegate(self.address))
        self.client.writeCharacteristic(self.characteristics[0].getHandle() + 1, b"\x01\x00", withResponse=True)
        self.client.writeCharacteristic(self.characteristics[3].getHandle() + 1, b"\x01\x00", withResponse=True)

    def login(self):
        self.characteristics[1].write(const.CREDENTIALS_MESSAGE, withResponse=True)

    def enable_data(self):
        self.characteristics[4].write(const.REALTIME_DATA_ENABLE_MESSAGE, withResponse=True)

    def enable_battery(self):
        self.characteristics[4].write(const.REQ_BATTERY_MESSAGE, withResponse=True)

    def set_deg_f(self):
        self.characteristics[4].write(const.UNITS_F_MESSAGE, withResponse=True)

    def read_temperature(self):
        return self.service.peripheral.readCharacteristic(self.characteristics[3].handle)
