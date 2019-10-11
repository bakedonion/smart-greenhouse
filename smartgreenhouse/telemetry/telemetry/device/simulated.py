"""
This module provides a selection of simulated devices, that can communicate
with an Azure IoT Hub.

"""

import threading
import datetime
import logging

from azure.iot.device import IoTHubDeviceClient, Message


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

