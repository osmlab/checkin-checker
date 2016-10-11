# -*- coding: utf-8 -*-
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
            {"id": 0, "tags": {"name": "Tanjong Pagar Plaza"}},
            {"id": 0, "tags": {"name": "Tanjong Pagar Food Centre"}},
            {"id": 0, "tags": {"name": "Tanjong Pagar Plaza"}},
            {"id": 1, "tags": {"name": "Tanjong Pagar"}},
        ]
        venue_name = "Tanjong Pagar"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(4, len(matches))
        self.assertEqual(1, matches[0][1]['id'])

    def test_match_filter_restaurant_no_match(self):
        possibilities = [
            {"id": 0, "tags": {"name": u"IJssalon"}},
            {"id": 0, "tags": {"name": u"Pathé Schouwburgplein"}},
            {"id": 0, "tags": {"name": u"Plaza"}},
            {"id": 0, "tags": {"name": u"Indonesia Satebar"}},
        ]
        venue_name = u"Has Döner Kebab"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(0, len(matches))

    def test_match_filter_waffle_shop(self):
        possibilities = [
            {"id": 0, "tags": {"name": u"Tariff Commission Building"}},
            {"id": 0, "tags": {"name": u"Foo Bar"}},
        ]
        venue_name = u"Lincoln's Waffle Shop"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(0, len(matches))

    def test_match_filter_front_street(self):
        possibilities = [
            {"id": 0, "tags": {"name": u"Brown Street"}},
            {"id": 0, "tags": {"name": u"Front Avenue"}},
        ]
        venue_name = u"Front Street"
        matches = filter_matches(venue_name, possibilities)

        self.assertEqual(0, len(matches))
