from webapp import app
from definitions import EVENT_HUB_CONNECTION_STRINGS
from webapp.utils.azure import SimpleMessageReceiver
import threading
import logging

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


if __name__ == "__main__":
    app.run()
