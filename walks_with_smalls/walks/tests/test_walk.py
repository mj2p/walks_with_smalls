import pytest
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.test import TestCase
from django.utils.text import slugify

from walks.models import Walk, get_sentinel_user

from faker import Faker

fake = Faker()


class TestWalk(TestCase):
    def setUp(self):
        self.name = fake.sentence()
        self.description = "\n".join(fake.paragraphs(nb=10))
        self.route = pytest.helpers.make_random_walk(10)
        self.walk = Walk.objects.create(
            name=self.name,
            description=self.description,
            submitter=get_sentinel_user(),
            route=self.route,
        )

    def test_walk_length(self):
        self.assertEqual(self.walk.route_length, D(m=self.route.length).mi)

    def test_walk_start(self):
        self.route.transform(4326)
        route_start = Point(
            srid=self.route.srid, x=self.route[0][0], y=self.route[0][1],
        )
        self.assertEqual(
            self.walk.start[0],
            round(self.walk.calculate_walk_start()[0], 6),
            round(route_start[0], 6),
        )
        self.assertEqual(
            self.walk.start[1],
            round(self.walk.calculate_walk_start()[1], 6),
            round(route_start[1], 6),
        )

    def test_walk_slug(self):
        self.assertEqual(self.walk.slug, slugify(self.name))
