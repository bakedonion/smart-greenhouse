from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# routes imports app -> bypass circular import
from . import routes
