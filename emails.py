from threading import Thread
from decorators import async
from flask.ext.mail import Message
from runserver import mail, app

@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body):

    msg = Message(subject, sender = sender, recipients = [recipients])
    msg.body = text_body
    thr = Thread(target = send_async_email, args=[msg])
    thr.start()