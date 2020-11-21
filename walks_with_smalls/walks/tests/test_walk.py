from random import randrange

from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from walks.models import Walk, get_sentinel_user


class TestWalk(TestCase):
    @staticmethod
    def _make_random_walk(num_points):
        return LineString(
            [
                Point(x=randrange(-180, 180), y=randrange(-90, 90))
                for _ in range(num_points)
            ]
        )

    def test_walk_length(self):
        route = self._make_random_walk(10)
        walk = Walk.objects.create(
            id=5000000,
            name="Test Walk",
            description="Test Walk Description",
            submitter=get_sentinel_user(),
            route=route,
        )

        route.transform(4326)
        self.assertEqual(walk.route_length, route.length)
