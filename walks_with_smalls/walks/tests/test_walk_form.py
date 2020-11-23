from http import HTTPStatus
from random import choice

import pytest
from django.test import TestCase
from django.urls import reverse

from users.models import User
from walks.forms import WalkForm
from walks.models import get_sentinel_user

from faker import Faker

fake = Faker()


class WalkFormUnitTests(TestCase):
    def setUp(self):
        self.name = fake.sentence()
        self.description = "\n".join(fake.paragraphs(nb=10))
        self.route = pytest.helpers.make_random_walk(10)

        self.correct_form = WalkForm(
            data={
                "name": self.name,
                "description": self.description,
                "route": self.route,
            },
            submitter=get_sentinel_user().pk,
        )
        self.correct_form.is_valid()

    def test_walk_name(self):
        # make sure the correct form has the name in cleaned data
        self.assertEqual(self.correct_form.cleaned_data["name"], self.name)

        # if the name is missing we should see that in the form error
        missing_name_form = WalkForm(
            data={
                "name": choice(["", None]),
                "description": self.description,
                "route": self.route,
            },
            submitter=get_sentinel_user().pk,
        )
        self.assertEqual(missing_name_form.errors["name"], ["This field is required."])

    def test_walk_description(self):
        # make sure the correct form has the name in cleaned data
        self.assertEqual(
            self.correct_form.cleaned_data["description"], self.description
        )

        # if the name is missing we should see that in the form error
        missing_description_form = WalkForm(
            data={
                "name": self.name,
                "description": choice(["", None]),
                "route": self.route,
            },
            submitter=get_sentinel_user().pk,
        )
        self.assertEqual(
            missing_description_form.errors["description"], ["This field is required."]
        )

    def test_walk_route(self):
        # make sure the correct form has the name in cleaned data
        self.assertEqual(self.correct_form.cleaned_data["route"], self.route)

        # if the name is missing we should see that in the form error
        missing_route_form = WalkForm(
            data={
                "name": self.name,
                "description": self.description,
                "route": choice(["", None]),
            },
            submitter=get_sentinel_user().pk,
        )
        self.assertEqual(
            missing_route_form.errors["route"],
            ["Please enter the walk route using the map"],
        )


class WalkCreateViewIntegrationTests(TestCase):
    def setUp(self):
        self.username = fake.user_name()
        self.password = fake.word()
        self.user = User.objects.create_user(
            username=self.username, email=fake.email(), password=self.password
        )

    def test_add_walk_form_no_login(self):
        response = self.client.get(reverse("walk-add"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302
        self.assertEqual(
            response["location"], f"{reverse('login')}?next={reverse('walk-add')}"
        )

    def test_add_walk_form(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("walk-add"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "<h2>Add a Walk</h2>", html=True)

    # def test_post_success(self):
    #     response = self.client.post(
    #         "/books/add/", data={"title": "Dombey and Son"}
    #     )
    #
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(response["Location"], "/books/")
    #
    # def test_post_error(self):
    #     response = self.client.post(
    #         "/books/add/", data={"title": "Dombey & Son"}
    #     )
    #
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     self.assertContains(response, "Use 'and' instead of '&'", html=True)
