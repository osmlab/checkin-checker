from checkinchecker.checker import filter_matches
from unittest import TestCase

class CheckerTests(TestCase):
    def test_match_filter_visulite(self):
        possibilities = [
            {"id": 0, "tags": {"name": "Taste of India"}},
            {"id": 0, "tags": {"name": "Staunton"}},
            {"id": 1, "tags": {"name": "Visulite Cinema"}},
        ]
        venue_name = "Visulite Cinema - Downtown Staunton"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(1, len(matches))
        self.assertEqual(1, matches[0][1]['id'])

    def test_match_filter_iad_airport(self):
        possibilities = [
            {"id": 0, "tags": {"name": "Dunkin' Donuts"}},
            {"id": 1, "tags": {"name": "Ronald Reagan Washington National Airport"}},
            {"id": 0, "tags": {"name": "Police"}},
            {"id": 0, "tags": {"name": "Faber News"}},
        ]
        venue_name = "Ronald Reagan Washington National Airport (DCA)"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(1, len(matches))
        self.assertEqual(1, matches[0][1]['id'])

    def test_match_filter_apartment(self):
        possibilities = [
            {"id": 0, "tags": {"name": "Berean Baptist Church"}},
            {"id": 0, "tags": {"name": "Church of Christ of Albina"}},
            {"id": 0, "tags": {"name": "Community Church of God"}},
            {"id": 1, "tags": {"name": "The Mason Williams"}},
        ]
        venue_name = "The Mason Williams"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(1, len(matches))
        self.assertEqual(1, matches[0][1]['id'])

    def test_match_filter_neighborhood(self):
        possibilities = [
            {"id": 0, "tags": {"name": "Berean Baptist Church"}},
            {"id": 0, "tags": {"name": "Church of Christ of Albina"}},
            {"id": 0, "tags": {"name": "Community Church of God"}},
            {"id": 1, "tags": {"name": "The Mason Williams"}},
        ]
        venue_name = "Tanjong Pagar"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(1, len(matches))
        self.assertEqual(1, matches[0][1]['id'])
