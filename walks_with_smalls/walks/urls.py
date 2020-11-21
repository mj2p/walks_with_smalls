from django.urls import path
from .views import (
    IndexSearch,
    Search,
    GetUserLocation,
    Results,
    WalkDetail,
    WalkCreate,
    WalkUpdate,
)

urlpatterns = [
    path("", IndexSearch.as_view(), name="index"),
    path("search/", Search.as_view(), name="search"),
    path("results/", Results.as_view(), name="results"),
    path("get-user-location/", GetUserLocation.as_view(), name="get-user-location"),
    path("walk/<str:username>/<slug:slug>/", WalkDetail.as_view(), name="walk-detail"),
    path("walk/add/", WalkCreate.as_view(), name="walk-add"),
    path(
        "walk/<str:username>/<slug:slug>/update/",
        WalkUpdate.as_view(),
        name="walk-update",
    ),
]
