import ssl
import logging
import smtplib
import traceback

from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pab.config import Config

APP_CONFIG = None

logger = logging.getLogger("pab.alert")
SSL_CONTEXT = ssl.create_default_context()


@contextmanager
def smtp(config: Config):
    with smtplib.SMTP(config.get("emails.host"), port=config.get("emails.port")) as _server:
        _server.starttls(context=SSL_CONTEXT)
        _server.login(config.get("emails.user"), config.get("emails.password"))
        yield _server


def alert_exception(exception, config: Config):
    content = "Error on PyAutoBlockchain:\n\n"
    content += ''.join(traceback.format_tb(exception.__traceback__))
    content += f"\n{type(exception).__name__}: {exception}"
    send_email(content, config)


def send_email(content, config: Config):
    if config.get("emails.enabled"):
        with smtp(config) as _server:
            msg = MIMEMultipart()
            msg['From'] = config.get("emails.user")
            msg['To'] = config.get("emails.recipient")
            msg['Subject'] = "Error on PyAutoBlockchain"
            msg.attach(MIMEText(content, 'plain'))
            _server.send_message(msg)
