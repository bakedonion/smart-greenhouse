"""
This module implements event handlers for an Azure Event Hub.

---

Functions:
    initiate_shutdown(): Sets the flag 'shutdown_initiated'.

Module variables:
    shutdown_initiated: A flag (threading.Event), that can be set to initiate the shutdown of all handlers.
    sleep_timer: All handlers sleep this long each loop or wait at most this long for a command.
"""

from azure.eventhub import EventHubClient, EventPosition, EventData, EventHubConsumer
from typing import List, Mapping, Any
import threading
import logging

shutdown_initiated = threading.Event()
sleep_timer = 0.1


def initiate_shutdown():
    """
    Sets the shutdown flag.
    """
    shutdown_initiated.set()


class SimpleMessageReceiver(threading.Thread):
    """
    A simple class to receive messages sent to an Azure Even Hub.
    """

    def __init__(self, connection_string: str, handler_name: str = 'MessageReceiver', **kwargs: Mapping[str, Any]):
        """
        Initializes a simple event receiver for an Event Hub.

        ---

        Args:
            connection_string: The connection string for the EventHub you wish to connect to.
            handler_name: Name of the handler.
            kwargs: For further possibilities see threading.Thread.
        """
        super().__init__(name=handler_name, kwargs=kwargs)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.NOTSET)

        self.event_hub_client = EventHubClient.from_connection_string(
            connection_string)

        partition_ids = self.event_hub_client.get_partition_ids()

        self.consumer = []
        self.running_consumers = []

        for partition_id in partition_ids:
            self.consumer.append(self.event_hub_client.create_consumer(
                '$default', partition_id, EventPosition("@latest", True)))

    def run(self):
        """
        Runs the simple message receiver. Starts a new thread for each partition consumer.
        """
        for consumer in self.consumer:
            consumer_thread = threading.Thread(
                name=self.name, target=self._consume_messages, args=(consumer,))
            consumer_thread.start()
            self.running_consumers.append(consumer_thread)

        for consumer_thread in self.running_consumers:
            consumer_thread.join()

        self.logger.info(f'shutdown')

    def _consume_messages(self, consumer: EventHubConsumer):
        """
        Comsumes the messages on an Event Hub.
        """
        while not shutdown_initiated.is_set():
            events: List[EventData] = consumer.receive(timeout=sleep_timer)

            for event in events:
                self.logger.info(
                    f'[Partition {consumer._partition:>{2}}]: {event.message}')

        consumer.close()

    @classmethod
    def from_connection_string(cls, connection_string: str) -> 'SimpleMessageReceiver':
        """
        Creates a simple event receiver based on the connection string and the delegate.

        ---

        Args:
            connection_string: The connection string for the EventHub you wish to connect to.

        Returns:
            A new simple message receiver.
        """
        return SimpleMessageReceiver(connection_string=connection_string)

