import logging
import os
import requests
from flask import Flask, request, render_template, json
from rq import Queue

from checkinchecker.worker import conn
from checkinchecker.util import send_email, setup_loghandlers
from checkinchecker.checker import foursquare_checkin_has_matches


# configuration
# DEBUG = True
SECRET_KEY = 'development key'
MAILGUN_URL_BASE = os.environ.get('MAILGUN_URL_BASE')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_API_DOMAIN = os.environ.get('MAILGUN_API_DOMAIN')
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT')


application = Flask(__name__)
application.config.from_object(__name__)
q = Queue(connection=conn)
logger = logging.getLogger('checker')
setup_loghandlers()


@application.route('/')
def index():
    callback_url = 'https://checkin-checker.dev.openstreetmap.us/auth/callback/foursquare'
    return render_template('index.html', callback_url=callback_url)


@application.route('/auth/callback/foursquare')
def foursquare_auth_callback():
    code = request.args.get('code')
    if code:
        logger.info("Exchanging code for access token")
        response = requests.get(
            "https://foursquare.com/oauth2/access_token",
            params=dict(
                client_id=FOURSQUARE_CLIENT_ID,
                client_secret=FOURSQUARE_CLIENT_SECRET,
                grant_type='authorization_code',
                redirect_uri='https://checkin-checker.dev.openstreetmap.us/auth/callback/foursquare',
                code=code,
            )
        )
        response.raise_for_status()
        access_token = response.json().get('access_token')
        logger.info("Got access token for user")

        response = requests.get(
            "https://api.foursquare.com/v2/users/self",
            params=dict(
                oauth_token=access_token,
                v='20151108',
            )
        )
        response.raise_for_status()
        user_data = response.json()['response']['user']
        email = user_data.get('contact', {}).get('email')
        if email:
            message = u"Hi {name},\n\n" \
                "You just connected your Foursquare account to Checkin Checker at https://checkin-checker.dev.openstreetmap.us. " \
                "If you ever want to disconnet, go to https://foursquare.com/settings/connections and remove the Checkin Checker app.\n\n" \
                "Checkin Checker".format(
                    name=user_data.get('firstName'),
                )
            send_email(email, "Welcome to Checkin Checker", message)

        message = u"A new checkin-checker user from Foursquare just connected.\n\n" \
            "Name: {name}\n" \
            "Foursquare page: https://foursquare.com/user/{user_id}\n".format(
                name=user_data.get('firstName'),
                user_id=user_data.get('id'),
            )
        send_email('ian@openstreetmap.us', "New Checkin Checker User", message)

    return render_template('auth_callback_foursquare.html')


@application.route('/hooks/foursquare', methods=['POST'])
def foursquare_webhook():
    checkin = json.loads(request.form.get('checkin'))
    user = json.loads(request.form.get('user'))
    q.enqueue(foursquare_checkin_has_matches, checkin, user)
    logger.info('Enqueued a webhook from a user')
    return 'OK'

if __name__ == '__main__':
    application.run()
