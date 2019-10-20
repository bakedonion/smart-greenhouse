# Smart Greenhouse

This project serves as a prove of concept. It is split up into two parts: _telemetry_ and _webapp_. _telemetry_ simulates IoT devices and send their mock data to an Azure IoT Hub. _webapp_ on the other hand presents the collected data in a simple webapp and showcases the use of direct method invocations.

## Requirements

Absolutely required dependencies are listed in [`requirements.txt`](./requirements.txt). Those dependecies are also split across [`telemetry/requirements.txt`](./telemetry/requirements.txt) and [`webapp/requirements.txt`](./webapp/requirements.txt), each listing the required packages to run their respective _main.py_.

In [`requirements-optional-azure-cli.txt`](./requirements-optional-azure-cli.txt) are further requirements listed, to use [`iot-hub-config.azcli`](./iot-hub-config.azcli).

## Run
Make sure you have the respective requirements installed. Then simply run `path/main.py`.

If you have `gunicorn` or a similar server installed you can use it for the webapp part, but make sure that it uses `eventlet` as their worker class. For gunicorn this would look like:

`gunicorn --bind=127.0.0.1:5000 --chdir webapp -k eventlet main:app`.

# Attribution
The resources contained under [`webapp/webapp/static/icons/fontawesome`](./webapp/webapp/static/icons/fontawesome) are licensed to [FontAwesome](https://fontawesome.com/license/free).
