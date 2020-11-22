import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance, Length
from django.contrib.gis.measure import D
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, F
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView

from .forms import WalkForm, ReadOnlyWalkRouteForm, SearchForm
from .models import Walk, PostCode, Attribute


class IndexSearch(View):
    @staticmethod
    def get(request):
        return render(request, "walks/index.html",)


class Search(FormView):
    template_name = "walks/results.html"
    form_class = SearchForm
    success_url = reverse_lazy("results")

    def form_valid(self, form):
        # populate the search dict on the session
        session_search = self.request.session.get("search", {})

        for search_parameter in form.fields:
            session_search[search_parameter] = form.cleaned_data[search_parameter]

        # set the search lat and long based on the lat long set on the session (if they exist)
        if form.cleaned_data["use_current_location"]:
            if self.request.session.get("lat") and self.request.session.get("long"):
                session_search["lat"] = self.request.session.get("lat")
                session_search["long"] = self.request.session.get("long")
            else:
                messages.add_message(
                    self.request, messages.ERROR, "Could not get your current location"
                )
                return redirect(self.request.session["redirect_to"])

        elif form.cleaned_data["postcode"]:
            try:
                postcode_obj = PostCode.objects.get(
                    postcode=form.cleaned_data["postcode"]
                )
            except PostCode.DoesNotExist:
                r = requests.get(
                    url=f"https://api.postcodes.io/postcodes/{form.cleaned_data['postcode']}"
                )

                try:
                    response = r.json()
                except TypeError:
                    messages.add_message(
                        self.request,
                        messages.ERROR,
                        "There was a problem when trying to look up the entered postcode",
                    )
                    return redirect(self.request.session["redirect_to"])

                if r.status_code != requests.codes.ok:
                    messages.add_message(
                        self.request, messages.WARNING, response.get("error")
                    )
                    return redirect(self.request.session["redirect_to"])

                lat = response.get("result", {}).get("latitude")
                long = response.get("result", {}).get("longitude")

                if not lat or not long:
                    messages.add_message(
                        self.request,
                        messages.ERROR,
                        "There was a problem getting location data from the entered postcode",
                    )
                    return redirect(self.request.session["redirect_to"])

                postcode_obj = PostCode.objects.create(
                    postcode=form.cleaned_data["postcode"], latitude=lat, longitude=long
                )

            session_search["lat"] = postcode_obj.latitude
            session_search["long"] = postcode_obj.longitude

        session_search["attributes"] = []

        for place_attribute in Attribute.objects.all():
            if form.cleaned_data[place_attribute.attribute]:
                session_search["attributes"].append(place_attribute.pk)

        self.request.session["search"] = session_search
        return super().form_valid(form)


class Results(ListView):
    model = Walk
    context_object_name = "walks"
    template_name = "walks/results.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # save the redirect link
        self.request.session["redirect_to"] = "results"
        # instantiate the search for and populate with initial data
        form = SearchForm()
        initial_data = {}

        for search_parameter in form.fields:
            if self.request.session.get("search", {}).get(search_parameter):
                initial_data[search_parameter] = self.request.session["search"][
                    search_parameter
                ]

        # update the initial data on the form
        form.initial = initial_data

        context["form"] = form
        context["attributes"] = Attribute.objects.values_list("attribute", flat=True)
        return context

    def get_queryset(self):
        # start off with all walks
        queryset = Walk.objects.all()

        # check we have search parameters in the session
        search_params = self.request.session.get("search", {})

        if (
            not search_params
            or not search_params.get("lat")
            or not search_params.get("long")
        ):
            # show all the walks if there are no search params to filter by
            return queryset

        # if here, we have a set of search params.
        # We can build a Point to search from
        search_location = Point(
            srid=4326,
            x=float(search_params.get("long")),
            y=float(search_params.get("lat")),
        )

        # we can annotate and filter
        # fmt: off
        return queryset.annotate(
            distance=Distance("start", search_location)
        ).annotate(
            attribute_match_count=Count(
                "attributes",
                filter=Q(attributes__in=search_params.get("attributes", [])),
            )
        ).filter(
            start__distance_lte=(
                search_location,
                D(mi=float(search_params.get("search_radius", 250))),
            )
        ).filter(
            route_length__lte=search_params.get("maximum_length", 500)
        ).order_by(
            "-attribute_match_count",
            "route_length",
            "distance",
        )
        # fmt: on

        return queryset


@method_decorator(csrf_exempt, name="dispatch")
class GetUserLocation(View):
    def post(self, request):
        request.session["lat"] = round(float(request.POST.get("lat")), 6)
        request.session["long"] = round(float(request.POST.get("long")), 6)
        return HttpResponse(status=201)


class SubmitterRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().submitter != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class WalkDetail(DetailView):
    model = Walk
    context_object_name = "walk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ReadOnlyWalkRouteForm(initial={"route": self.object.route})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        search_params = self.request.session.get("search", {})

        if search_params.get("lat") and search_params.get("long"):
            search_location = Point(
                srid=4326,
                x=float(search_params.get("long")),
                y=float(search_params.get("lat")),
            )
            return queryset.annotate(
                distance_from=Distance(F("start"), search_location)
            )

        return queryset


class WalkCreate(LoginRequiredMixin, CreateView):
    model = Walk
    form_class = WalkForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attributes"] = Attribute.objects.values_list("attribute", flat=True)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["submitter"] = self.request.user.pk
        return kwargs


class WalkUpdate(LoginRequiredMixin, SubmitterRequiredMixin, UpdateView):
    model = Walk
    form_class = WalkForm
    context_object_name = "walk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attributes"] = Attribute.objects.values_list("attribute", flat=True)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["submitter"] = self.request.user.pk
        return kwargs
