from flask import Flask
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('rcrdkeeper.settings')

mail = Mail(app)

from rcrdkeeper import views