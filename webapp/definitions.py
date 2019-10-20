import os


def read_connection_string_file(file: str, keyname: str):
    connection_strings = {}

    with open(file) as f:
        lines = f.read().splitlines()

        for line in lines:
            if line.strip().startswith('#'):
                continue

            for key, _, value in (keyvalue.partition('=') for keyvalue in line.split(';')):
                if key.lower() == keyname.lower():
                    connection_strings[value] = line
                    break

    return connection_strings


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

EVENT_HUB_CONNECTION_STRINGS_FILE = os.path.join(
    ROOT_DIR,  'event-hub-connection-strings')
EVENT_HUB_CONNECTION_STRINGS = read_connection_string_file(
    EVENT_HUB_CONNECTION_STRINGS_FILE, keyname='SharedAccessKeyName')

IOT_HUB_CONNECTION_STRINGS_FILE = os.path.join(
    ROOT_DIR, 'iot-hub-connection-strings')
IOT_HUB_CONNECTION_STRINGS = read_connection_string_file(
    IOT_HUB_CONNECTION_STRINGS_FILE, keyname='SharedAccessKeyName')
