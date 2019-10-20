from webapp import app
from webapp.routes import socketio
from definitions import EVENT_HUB_CONNECTION_STRINGS
from webapp.utils.azure import SimpleMessageReceiver
import threading
import logging
import eventlet

eventlet.monkey_patch()

app_name = 'webapp'
threading.current_thread().setName(app_name)

logger = logging.getLogger(app_name)
logger.setLevel(level=logging.DEBUG)
sh = logging.StreamHandler()
sh_formatter = logging.Formatter(
    fmt='[{asctime}] [{levelname:^8}]: <{threadName}>: {message}',
    style='{')
sh.setFormatter(sh_formatter)
logger.addHandler(sh)

simple_message_receiver = SimpleMessageReceiver(
    EVENT_HUB_CONNECTION_STRINGS['service'], socketio=socketio, daemon=True)
simple_message_receiver.start()


if __name__ == "__main__":
    socketio.run(app)
