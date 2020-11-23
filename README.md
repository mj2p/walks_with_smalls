# Walks with Smalls
### Share local knowledge and walk more!

---
![test_deploy](https://github.com/mj2p/walks_with_smalls/workflows/test_deploy/badge.svg)
[![codecov](https://codecov.io/gh/mj2p/walks_with_smalls/branch/master/graph/badge.svg)](https://codecov.io/gh/mj2p/walks_with_smalls)
---

**Walks with Smalls** is a site for sharing information about child friendly walks.
The aim is to make getting out with small children less of a chore and to share local information of good places to take them.

#### Technology
**Walks with Smalls** is written mainly in Python and uses the Django web framework.
It also utilises GeoDjango for geo-spacial lookups and calculations.
It is intended to run inside Docker containers for which a Dockerfile and docker-compose.yml scripts are supplied.

External data comes from:
[OpenCage](https://opencagedata.com/) for reverse geocoding lookups (fetching address information from a latitude/longitude)
[Postcodes.io](https://postcodes.io/) for fetching location data from a postcode.
[OpenStreetMap](https://www.openstreetmap.org/copyright) for displaying interactive maps.

#### Development
To get up and running for development you will need pipenv and docker-compose installed.

First, download the dependencies:
`pipenv sync --dev`

The docker-compose scripts expect a file containing the site secrets.
First create the file in the expected directory:
`mkdir -p .config; touch .config/.env.dev`
Then populate the file with the following secrets:
```
POSTGRES_DB=<the name of the database>
POSTGRES_USER=<a username for the database user>
POSTGRES_PASSWORD=<a password for the database user>
POSTGRES_HOST=<the host the database can be found on. This will be 'db' if using the supplied docker-compose scripts>
OPENCAGE_API_KEY=<an api key from the OpenCage service>
SECRET_KEY=<a large random string for django to use when signing session data>
```

This command will then create a running container with the site code mounted in a volume:
`pipenv run docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`
(on first run the database needs to initialise so the web app may fail to connect. Exit the run and restart and it should work)

Once it's running you will need to migrate the database:
`pipenv run docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm web pipenv run python walks_with_smalls/manage.py migrate`
And create a superuser:
`pipenv run docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm web pipenv run python walks_with_smalls/manage.py createsuperuser`
