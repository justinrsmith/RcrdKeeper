from flask import Flask
import os	
from flask.ext.mail import Mail
from time import gmtime, strftime

UPLOAD_FOLDER = 'rcrdkeeper/static/user_albums/'


app = Flask(__name__)
app.secret_key = 'fsadfsdafsafsdgrberbebebe'
app.config['SERVER_NAME'] = 'localhost:4000'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'rcrdkeeper@gmail.com',
    MAIL_PASSWORD = '**'
)

mail = Mail(app)

from rcrdkeeper import views