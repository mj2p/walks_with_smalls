# Generated by Django 3.1.3 on 2020-11-20 10:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("walks", "0013_auto_20201119_2023"),
    ]

    operations = [
        migrations.AddField(
            model_name="walk",
            name="slug",
            field=models.SlugField(default="bleh", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="walk",
            name="reverse_geocode_cache_time",
            field=models.DateTimeField(
                default=datetime.datetime(2018, 12, 1, 10, 46, 57, 317715, tzinfo=utc)
            ),
        ),
    ]
