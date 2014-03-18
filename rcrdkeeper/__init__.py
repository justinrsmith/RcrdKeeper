from flask import Flask
import os	
from flask.ext.mail import Mail
from time import gmtime, strftime

UPLOAD_FOLDER = 'rcrdkeeper/static/user_albums/'


app = Flask(__name__)
app.secret_key = 'some_secret' + strftime("%Y-%m-%d %H:%M:%S", gmtime())
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

from rcrdkeeper import views