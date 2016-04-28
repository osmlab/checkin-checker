from fuzzywuzzy import fuzz
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
query_timeout = 15

def foursquare_checkin_has_matches(checkin, user):
    venue = checkin.get('venue')
    venue_name = venue.get('name')

    categories = venue.get('categories')
    for category in categories:
        if category.get('name').endswith('(private)'):
            logger.info("Skipping checkin at private venue")
            return

    user_email = user.get('contact', {}).get('email')
    if not user_email:
        logger.warn("This checkin didn't have a user email, so I didn't do anything")
        return

    # Send emails for test pushes to me
    if user.get('id') == '1':
        user_email = 'ian@openstreetmap.us'

    query_parts = []
    for t in tags_to_check:
        for i in ('node', 'way', 'relation'):
            query_part = '{prim_type}["{tag}"](around:{radius},{lat},{lng});'.format(
                prim_type=i,
                tag=t,
                radius=radius_meters,
                lat=round(venue.get('location').get('lat'), 6),
                lng=round(venue.get('location').get('lng'), 6),
            )
            query_parts.append(query_part)

    query = '[out:json][timeout:{}];({});out body;'.format(
            query_timeout,
            ''.join(query_parts),
        )

    logger.info("Querying Overpass with: %s", query)

    response = requests.post('https://overpass-api.de/api/interpreter', data=query)

    response.raise_for_status()

    osm = response.json()
    elements = osm.get('elements')

    logger.info("Found %s things on Overpass", len(elements))

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

        distance = fuzz.partial_ratio(venue_name, osm_name)

        return distance

    # Attach match score to each element with a tuple
    potential_matches = [(match_amount(elem), elem) for elem in elements]
    # Sort the tuples based on their match score
    potential_matches = sorted(potential_matches, key=lambda e: e[0], reverse=True)
    # Only pay attention to the tuples that are decent matches
    potential_matches = filter(lambda p: p[0] > 60, potential_matches)

    if not potential_matches:
        logger.info("No matches! Send an e-mail to %s", user_email)

        message = u"""Hi {name},

You checked in at {venue_name} on Foursquare but that location doesn't seem to exist in OpenStreetMap. You should consider adding it!

In fact, here's a direct link to the area in your favorite editor:
https://www.openstreetmap.org/edit?zoom=19&lat={mlat}&lon={mlon}

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
        send_email(user_email, "Your Recent Foursquare Checkin Isn't On OpenStreetMap", message)
    else:
        logger.info(u"Matches: {}".format(u', '.join(map(lambda i: '{}/{} ({:0.2f})'.format(i[1]['type'], i[1]['id'], i[0]), potential_matches))))
        best_match_score, best_match = potential_matches[0]

        if best_match_score > 80:
            logger.info(u"A really great match found: %s/%s (%0.2f)", best_match['type'], best_match['id'], best_match_score)

            tags = best_match['tags']
            questions = []
            if 'addr:housenumber' in tags:
                questions.append(" - Is the housenumber still '{}'?".format(tags['addr:housenumber']))
            else:
                questions.append(" - What is the housenumber?")
            if 'addr:street' in tags:
                questions.append(" - Is the venue still on '{}'?".format(tags['addr:street']))
            else:
                questions.append(" - What is the street name?")
            if 'phone' in tags:
                questions.append(" - Is the phone number still '{}'?".format(tags['phone']))
            else:
                questions.append(" - What is the phone number?")

            message = u"""Hi {name},

Your recent checkin to {venue_name} seems to match something in OpenStreetMap. While you're visiting this place, try collecting these missing attributes for OpenStreetMap:

{questions}

If you want, you can reply to this email and Ian will make these changes, or you can save your email as a draft/note to yourself for later.

If you'd like to edit the OSM object directly, use this edit link:
https://www.openstreetmap.org/edit?{osm_type}={osm_id}

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
                osm_type=best_match['type'],
                osm_id=best_match['id'],
                questions='\n'.join(questions),
                email=user_email,
            )

            send_email(user_email, "Your Recent Foursquare Checkin Is On OpenStreetMap!", message)
