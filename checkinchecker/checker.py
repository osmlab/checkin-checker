import editdistance
import requests
import logging

from util import send_email

logger = logging.getLogger(__name__)


def foursquare_checkin_has_matches(checkin, user):
    venue = checkin.get('venue')
    venue_name = venue.get('name')

    categories = venue.get('categories')
    for category in categories:
        if category.get('name').endswith('(private)'):
            logger.info("Skipping checkin at private venue")
            return

    query = '[out:json][timeout:5];(' \
        'node["name"](around:100.0,{lat},{lng});' \
        'way["name"](around:100.0,{lat},{lng});' \
        'relation["name"](around:100.0,{lat},{lng});' \
        ');out body;'.format(
            lat=venue.get('location').get('lat'),
            lng=venue.get('location').get('lng'),
        )

    response = requests.post('https://overpass-api.de/api/interpreter', data=query)

    response.raise_for_status()

    osm = response.json()
    elements = osm.get('elements')

    def is_match(osm_obj):
        element_name = osm_obj.get('tags').get('name')
        distance = editdistance.eval(venue_name, element_name)
        edit_pct = (float(distance) / max(len(venue_name), len(element_name))) * 100.0

        # print "{} -- {} ({:0.1f}%)".format(venue_name, element_name, edit_pct)

        return edit_pct < 50

    potential_matches = filter(is_match, elements)

    if not potential_matches:
        user_email = user.get('contact', {}).get('email')
        logger.info("No matches! Send an e-mail.")
        message = """Hi {name},

You checked in at {venue_name} on Foursquare but that location doesn't seem to exist in OpenStreetMap. You should consider adding it near http://osm.org/?zoom=17&mlat={mlat}&mlon={mlon}!

-Checkin Checker
(Reply to this e-mail for feedback/questions. Uninstall at https://foursquare.com/settings/connections to stop these e-mails.)""".format(
            name=user.get('firstName', 'Friend'),
            venue_name=venue_name,
            mlat=round(venue.get('location').get('lat'), 6),
            mlon=round(venue.get('location').get('lng'), 6),
            email=user_email,
        )
        if user_email:
            send_email(user_email, "Your Recent Foursquare Checkin Isn't On OpenStreetMap", message)
    else:
        logger.info("Matches: {}".format(', '.join(map(lambda i: i.get('tags').get('name'), potential_matches))))
