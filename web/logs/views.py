from django.shortcuts import render
from django.views.generic import TemplateView
import datetime


class IndexView(TemplateView):
    template_name = "logs/index.html"