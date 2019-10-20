#!/usr/bin/env python

"""
This module is used to simluate telemetry.
"""

from definitions import DEVICE_CONNECTION_STRINGS
import telemetry.device.simulated as SimulatedDevices
import threading
import logging

app_name = 'telemetry'
threading.current_thread().setName(app_name)

logger = logging.getLogger(app_name)
logger.setLevel(level=logging.DEBUG)
sh = logging.StreamHandler()
sh_formatter = logging.Formatter(
    fmt='[{asctime}] [{levelname:^8}]: <{threadName}>: {message}',
    style='{')
sh.setFormatter(sh_formatter)
logger.addHandler(sh)

logger.info('starting simulated devices, press Ctrl-C to exit')
running_devices = []

for device_id, connection_string in DEVICE_CONNECTION_STRINGS.items():
    device_type, _, _ = device_id.partition('-')
    device_to_use = getattr(SimulatedDevices, device_type)

    if device_to_use:
        device = device_to_use(device_id, connection_string)
        device.start()
        running_devices.append(device)
    else:
        logger.warning(f"No simulated device '{device_type}' exists.")

interrupt_event = threading.Event()

try:
    interrupt_event.wait()
except KeyboardInterrupt:
    logger.info("received Ctrl-C: initiate shutdown for simulated devices")
    SimulatedDevices.initiate_shutdown()

for device in running_devices:
    device.join()
