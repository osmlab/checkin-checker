import editdistance
import requests
import logging

from util import send_email

logger = logging.getLogger('checker')

tags_to_check = [
    'name',
    'alt_name',
    'loc_name',
    'official_name',
    'short_name',
]
radius_meters = 500.0

def foursquare_checkin_has_matches(checkin, user):
    venue = checkin.get('venue')
    venue_name = venue.get('name')

    categories = venue.get('categories')
    for category in categories:
        if category.get('name').endswith('(private)'):
            logger.info("Skipping checkin at private venue")
            return

    query_parts = []
    for t in tags_to_check:
        for i in ('node', 'way', 'relation'):
            query_part = '{prim_type}["{tag}"](around:{radius},{lat},{lng});'.format(
                prim_type=i,
                tag=t,
                radius=radius_meters,
                lat=venue.get('location').get('lat'),
                lng=venue.get('location').get('lng'),
            )
            query_parts.append(query_part)

    query = '[out:json][timeout:5];({});out body;'.format(
            ''.join(query_parts),
        )

    response = requests.post('https://overpass-api.de/api/interpreter', data=query)

    response.raise_for_status()

    osm = response.json()
    elements = osm.get('elements')

    def match_amount(osm_obj):
        osm_name = None
        tags = osm_obj.get('tags')
        for t in tags_to_check:
            osm_name = tags.get(t)
            if osm_name:
                break

        if not osm_name:
            logger.warn("OSM object %s/%s matched but no name tags matched", osm_obj['type'], osm_obj['id'])
            return

        distance = editdistance.eval(venue_name, osm_name)
        edit_pct = float(distance) / max(len(venue_name), len(osm_name))

        return edit_pct

    potential_matches = sorted(elements, key=match_amount)
    most_likely_matches = filter(lambda p: p > 50, potential_matches)

    if not most_likely_matches:
        user_email = user.get('contact', {}).get('email')
        logger.info("No matches! Send an e-mail.")
        message = u"""Hi {name},

You checked in at {venue_name} on Foursquare but that location doesn't seem to exist in OpenStreetMap. You should consider adding it near https://openstreetmap.org/?zoom=17&mlat={mlat}&mlon={mlon}!

In fact, here's a direct link to the area in your favorite editor:
https://www.openstreetmap.org/edit?zoom=17&lat={mlat}&lon={mlon}

To remind you where you went, here's a link to your checkin. Remember that you should not copy from external sources (like Foursquare) when editing.
https://foursquare.com/user/{user_id}/checkin/{checkin_id}

-Checkin Checker
(Reply to this e-mail for feedback/questions. Uninstall at https://foursquare.com/settings/connections to stop these e-mails.)""".format(
            name=user.get('firstName', 'Friend'),
            venue_name=venue_name,
            user_id=user['id'],
            checkin_id=checkin['id'],
            mlat=round(venue.get('location').get('lat'), 6),
            mlon=round(venue.get('location').get('lng'), 6),
            email=user_email,
        )
        if user_email:
            send_email(user_email, "Your Recent Foursquare Checkin Isn't On OpenStreetMap", message)
    else:
        logger.info(u"Matches: {}".format(u', '.join(map(lambda i: '{}/{}'.format(i['type'], i['id']), potential_matches))))
