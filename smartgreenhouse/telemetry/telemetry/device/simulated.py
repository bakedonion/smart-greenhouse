"""
This module provides a selection of simulated devices, that can communicate
with an Azure IoT Hub.

---

Functions:
    initiate_shutdown(): Sets the flag 'shutdown_initiated'.

Module variables:
    shutdown_initiated: A flag (threading.Event), that can be set to initiate the shutdown of all devices.
    sleep_timer: All device threads sleep this long each loop or wait at most this long for a command.
"""

import threading
import datetime
import logging
import random
import time
import json

from azure.iot.device import IoTHubDeviceClient, Message

shutdown_initiated = threading.Event()
sleep_timer = 0.1


def initiate_shutdown():
    """
    Sets the shutdown flag.
    """
    shutdown_initiated.set()


class Device(threading.Thread):
    """
    Abstract base class for a simulated device, that can communicate with an
    Azure IoT Hub.

    ---

    The device can mock measured sensor data and send it to the hub. Likewise
    it can receive messages from the hub. The device listens for messages in
    an extra daemonic thread.

    ---

    Attributes:
        device_id: A string representing the device's id, with which it is registered at the hub.
        connection_string: The connection string, that is used to connect to the hub.
        interval_in_seconds: Frequency, at which to send data.
        client: An IoTHubDeviceClient, that handles the communication with the hub.
    """

    def __init__(self, device_id: str, connection_string: str, interval_in_secs: int = 0):
        """
        Initializes the device's id and it's connection string with the given
        values and creates the communication client.

        ---

        Args:
            device_id: The device's id.
            connection_string: The devices connection string.
        """
        # init threading.Thread
        super().__init__(name=device_id)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.NOTSET)

        self.device_id = device_id
        self.connection_string = connection_string
        self.interval_in_secs = interval_in_secs
        self.last_msg_at = datetime.datetime.fromordinal(1)
        self.client = IoTHubDeviceClient.create_from_connection_string(
            connection_string)

    def run(self):
        """
        Starts a thread to receive incoming commands.

        Prints info about starting and stopping of the device to console and
        calls run_loop().
        """
        self.logger.info('starting')
        self.run_loop()
        self.logger.info('shutdown')

    def run_loop(self):
        """
        This method is called by run(). Can be implemented in a subclass.
        """
        pass

    def send_msg(self, msg: str):
        """
        Sends a message to the Azure IoT Hub, also prints the message. Can be
        implemented in a subclass.

        ---

        Args:
            msg: The message to send.
        """
        msg = Message(msg)
        self.client.send_message(msg)

        self.logger.info(msg)


class SensorDevice(Device):
    """
    Abstract base class for a simulated a device, that is mainly used to send
    measurements in shorter intervals to the hub.
    """

    def __init__(self, device_id: str, connection_string: str, interval_in_secs: int = 5):
        super().__init__(device_id, connection_string, interval_in_secs)

    def run_loop(self):
        """
        Calls send_data() every interval_in_secs seconds.
        """
        while not shutdown_initiated.is_set():
            if (datetime.datetime.now() - self.last_msg_at).total_seconds() >= self.interval_in_secs:
                self.send_data()
                self.last_msg_at = datetime.datetime.now()

            time.sleep(sleep_timer)

    def send_data(self):
        """
        Sends the devices sensor data to the hub. Can be implemented in a
        subclass.
        """
        pass


class ControllerDevice(Device):
    """
    Abstract base class for a simulated a device, that is mainly used to
    control a physical object, based on commands received from the hub.

    It normally only sends a message to the hub, to notify succesful
    execution of commands or when it encounters a problem.
    """

    def __init__(self, device_id: str, connection_string: str, interval_in_secs: int = 15):
        super().__init__(device_id, connection_string, interval_in_secs)

    def run_loop(self):
        while not shutdown_initiated.is_set():
            time.sleep(sleep_timer)


class SoilSensorsDevice(SensorDevice):
    """
    Simulates a device with different sensors to measure soil quality.
    Measures the soil's humidity/moisture and pH.
    """

    # base values for sensor data to mock measurements
    base_vwc = 32
    base_pH = 5.4

    def get_soil_humidity(self) -> int:
        """
        Gets the reading from the sensor, that measures the soil's volumetric
        water content in percent.

        ---

        Returns:
            vwc_in_percent
        """
        self.base_vwc = self.base_vwc - random.randint(1, 3)
        return self.base_vwc

    def get_soil_pH(self) -> float:
        """
        Gets the reading from the sensor, that measures the soil's pH..

        ---

        Returns:
            pH
        """
        return round(SoilSensorsDevice.base_pH + random.random() * 1.4, 1)

    def send_data(self):
        _, _, garden_bed_num = self.device_id.rpartition('-')

        vwc_in_percent = self.get_soil_humidity()
        pH = self.get_soil_pH()

        msg = json.dumps({
            'info_group': f'garden-bed-{garden_bed_num}',
            'measurements': {
                'vwc_in_percent': vwc_in_percent,
                'pH': pH
            }
        })

        self.send_msg(msg)


class AirSensorsDevice(SensorDevice):
    """
    Simulates a device with different sensors to measure relative air humidity
    and temperature.
    """

    # base values for sensor data to mock measurements
    base_humidity = 35
    base_temperature = 22

    def get_relative_air_humidity(self) -> int:
        """
        Gets the reading from the sensor, that measures the relative air
        humidity in percent.

        ---

        Returns:
            relative_air_humidity_in_percent
        """
        return self.base_humidity + random.randint(0, 35)

    def get_temperature(self) -> float:
        """
        Gets the reading from the sensor, that measures the temperature in
        celcius.

        ---

        Returns:
            temperature_in_celsius
        """
        return round(self.base_temperature + random.random() * 10, 1)

    def send_data(self):
        humidity_in_percent = self.get_relative_air_humidity()
        temperature_in_celsius = self.get_temperature()

        msg = json.dumps({
            'info_group': 'general-info',
            'measurements': {
                'relative_air_humidity_in_percent': humidity_in_percent,
                'temperature_in_celsius': temperature_in_celsius
            }
        })

        self.send_msg(msg)

