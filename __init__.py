from flask import Flask
from flask.ext.mail import Mail

app = Flask(__name__)
app.secret_key = 'some_secret'
app.config.from_object(__name__)

mail = Mail(app)