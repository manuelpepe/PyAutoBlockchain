"""
Module temporarily disabled
"""

import ssl
import logging
import smtplib
import traceback

from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#from pab.config import APP_CONFIG
APP_CONFIG = None

logger = logging.getLogger("pab.alert")
SSL_CONTEXT = ssl.create_default_context()


@contextmanager
def smtp():
    with smtplib.SMTP(APP_CONFIG.get("emails.host"), port=APP_CONFIG.get("emails.port")) as _server:
        _server.starttls(context=SSL_CONTEXT)
        _server.login(APP_CONFIG.get("emails.address"), APP_CONFIG.get("emails.password"))
        yield _server


def alert_exception(exception):
    content = "Error on PyAutoBlockchain:\n\n"
    content += ''.join(traceback.format_tb(exception.__traceback__))
    content += f"\n{type(exception).__name__}: {exception}"
    send_email(content)


def send_email(content):
    if APP_CONFIG.get("emails.enabled"):
        with smtp() as _server:
            msg = MIMEMultipart()
            msg['From'] = APP_CONFIG.get("emails.address")
            msg['To'] = APP_CONFIG.get("emails.recipient")
            msg['Subject'] = "Error on PyAutoBlockchain"
            msg.attach(MIMEText(content, 'plain'))
            _server.send_message(msg)
