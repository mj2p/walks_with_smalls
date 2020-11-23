from random import uniform

import pytest
from django.contrib.gis.geos import LineString, Point


pytest_plugins = ["helpers_namespace"]


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.helpers.register
def make_random_walk(num_points):
    return LineString(
        [
            Point(x=round(uniform(-180, 180), 6), y=round(uniform(-90, 90), 6))
            for _ in range(num_points)
        ],
        srid=4326,
    )
