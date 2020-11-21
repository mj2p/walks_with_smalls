from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.urls import reverse
from django.utils.timezone import now

from users.models import User

from opencage.geocoder import OpenCageGeocode, RateLimitExceededError


def get_sentinel_user():
    """
    Get or create a user to act as a placeholder is the user removes their account
    """
    return get_user_model().objects.get_or_create(username="deleted")[0]


class Attribute(models.Model):
    """
    Attributes are things like "Dog Friendly".
    They allow walks to be filtered in the search
    """

    attribute = models.CharField(max_length=250, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.attribute


class Walk(models.Model):
    """
    A Walk contains the route of the walk and all location data about the start location
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    start = models.PointField(blank=True, null=True)
    route = models.LineStringField()
    submitter = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    route_length = models.FloatField(
        help_text="The length of the walk in miles", default=0
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Reverse Geocoding from OpenCage
    reverse_geocode_cache_time = models.DateTimeField(blank=True, null=True)
    # annotations
    what3words = models.CharField(max_length=100, blank=True, null=True)
    geohash = models.CharField(max_length=50, blank=True, null=True)
    # components
    continent = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)
    road = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=100, blank=True, null=True)
    formatted = models.CharField(max_length=500, blank=True, null=True)

    attributes = models.ManyToManyField(Attribute, blank=True)

    def get_absolute_url(self):
        return reverse(
            "walk-detail",
            kwargs={"username": self.submitter.username, "slug": self.slug},
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        initial_start = self.start
        super().save(*args, **kwargs)

        # Check if the start location has changed
        start_location_changed = False

        if not self.start:
            self.start = self.calculate_walk_start()
            start_location_changed = True

        if self.start != initial_start:
            start_location_changed = True

        # check if the cache_has expired
        if self.reverse_geocode_cache_time is None:
            cache_expired = True
        else:
            cache_expired = self.reverse_geocode_cache_time < (
                now() - timedelta(days=180)
            )

        # update the location details if we need to
        if start_location_changed or cache_expired:
            if settings.OPENCAGE_API_KEY:
                geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)

                try:
                    results = geocoder.reverse_geocode(
                        round(self.start[1], 6),
                        round(self.start[0], 6),
                        language="en",
                        limit=1,
                    )

                    if results and len(results):
                        self.what3words = (
                            results[0].get("annotations").get("what3words").get("words")
                        )
                        self.geohash = results[0].get("annotations").get("geohash")
                        self.continent = results[0].get("components").get("continent")
                        self.country = results[0].get("components").get("country")
                        self.state = results[0].get("components").get("state")
                        self.county = results[0].get("components").get("county")
                        self.city = results[0].get("components").get("city")
                        self.suburb = results[0].get("components").get("suburb")
                        self.road = results[0].get("components").get("road")
                        self.postcode = results[0].get("components").get("postcode")
                        self.formatted = results[0].get("formatted")

                        self.reverse_geocode_cache_time = now()
                        super().save(*args, **kwargs)

                except RateLimitExceededError as e:
                    print(e)

        self.route.transform(3857)
        self.route_length = D(m=self.route.length).mi
        super().save(*args, **kwargs)

    def calculate_walk_start(self):
        return Point(srid=self.route.srid, x=self.route[0][0], y=self.route[0][1],)


class PostCode(models.Model):
    postcode = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.postcode
