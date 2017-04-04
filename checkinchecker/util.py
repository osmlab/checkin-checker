import logging
import os
import requests


def setup_loghandlers(level='INFO'):
    logger = logging.getLogger('checker')

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                                      datefmt='%H:%M:%S')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def send_email(to, subject, body):
    logger = logging.getLogger('checker')

    logger.info("Send email '%s' to %s", subject, to)
    response = requests.post(
        'https://api.mailgun.net/v3/{}/messages'.format(os.environ.get('MAILGUN_API_DOMAIN')),
        auth=('api', os.environ.get('MAILGUN_API_KEY')),
        data={
            "from": "Checkin Checker <ian@openstreetmap.us>",
            "to": to,
            "subject": subject,
            "text": body,
        }
    )
    logger.info("Send email '%s' to %s. Response %s.", subject, to, response.status_code)
    response.raise_for_status()
