from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("logs/", include("logs.urls"))
]
