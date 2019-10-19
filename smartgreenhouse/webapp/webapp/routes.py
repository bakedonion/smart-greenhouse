from . import app
from flask import render_template
from definitions import IOT_HUB_CONNECTION_STRINGS
from webapp.utils.azure import SimpleDirectMethodHandler

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

