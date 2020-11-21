from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Walk, Attribute, PostCode


@admin.register(Walk)
class WalkAdmin(OSMGeoAdmin):
    list_display = ("name", "start", "route_length")
    exclude = ["start"]
    readonly_fields = [
        "route_length",
        "what3words",
        "geohash",
        "country",
        "state",
        "county",
        "city",
        "suburb",
        "road",
        "postcode",
        "formatted",
    ]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("attribute", "description")


@admin.register(PostCode)
class PostCodeAdmin(admin.ModelAdmin):
    list_display = ("postcode", "latitude", "longitude")
