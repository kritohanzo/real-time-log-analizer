from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("users/", include("users.urls")),
    path("logs/", include("logs.urls")),
    path("", RedirectView.as_view(url="logs/")),
]
