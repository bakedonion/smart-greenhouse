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

DEVICE_CONNECTION_STRINGS_FILE = os.path.join(
    ROOT_DIR, 'device-connection-strings')
DEVICE_CONNECTION_STRINGS = read_connection_string_file(
    DEVICE_CONNECTION_STRINGS_FILE, keyname='DeviceId')
