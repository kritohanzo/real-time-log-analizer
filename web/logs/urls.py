from django.contrib import admin
from django.urls import path, include
from logs.views import IndexView
from django.contrib.auth.decorators import login_required

app_name = "logs"

urlpatterns = [
    path("", login_required(IndexView.as_view()), name="index")
]
