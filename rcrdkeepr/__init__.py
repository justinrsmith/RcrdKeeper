from flask import Flask
import os	
from flask.ext.mail import Mail

app = Flask(__name__)
app.secret_key = 'some_secret'
app.config.from_object(__name__)

app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'flasktesting33@gmail.com',
    MAIL_PASSWORD = 'testpw2013'
)

mail = Mail(app)

from rcrdkeepr import views