from . import app
from flask import render_template
from flask_socketio import SocketIO
from definitions import IOT_HUB_CONNECTION_STRINGS
from webapp.utils.azure import SimpleDirectMethodHandler

async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)

simple_direct_method_handler = SimpleDirectMethodHandler.create_from_connection_string(
    IOT_HUB_CONNECTION_STRINGS['service'])

contact_info = {
    'name': 'John Doe',
    'email': 'john.doe@email.com',
    'github': 'bakedonion'
}


@app.context_processor
def inject_contact_info():
    return {'title': 'Smart Greenhouse', 'smart_greenhouse_contact_info': contact_info}


@app.route('/')
def index():
    return render_template('index.html', page_title='Smart Greenhouse')


@socketio.on('direct_method_event')
def direct_method_event(message):
    url = message.get('url', '')
    method_name = message.get('method_name', '')
    arguments = message.get('arguments', {})

    socketio.start_background_task(target=socketio.emit(
        'direct_method_response', simple_direct_method_handler.invoke_direct_method(url=url, method_name=method_name, arguments=arguments)))
