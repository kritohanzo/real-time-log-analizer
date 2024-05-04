from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("auth/", include("users.urls")),
    path("logs/", include("logs.urls")),
    path("", RedirectView.as_view(url="logs/"))
]
