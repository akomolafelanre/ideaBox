from flask.ext.mail import Message
from app import mail, app
from threading import Thread
from .decorators import async

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = text_body
	msg.html = html_body
	mail.send(msg)