from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django import views
import datetime
from logs.forms import LogFileForm, LogTypeForm
from logs.models import LogFile, LogType, SearchPattern


class MainPageView(TemplateView):
    template_name = "logs/index.html"


# Log File Views


class LogFileListView(views.View):
    def get(self, request, *args, **kwargs):
        log_files = LogFile.objects.all()
        return render(request, template_name="logs/log-files/log-files-list.html", context={"log_files": log_files})


class LogFileAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = LogFileForm()
        return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogFileForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form})
        LogFile.objects.create(**form.cleaned_data)
        return render(request, template_name="success.html", context={"message": "Вы успеншо добавили лог-файл!"})


class LogFileDetailView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = LogFile.objects.all(id=log_file_id)
        return render(request, template_name="logs/log-files/log-files-list.html", context={"log_file": log_file})


class LogFileEditView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        form = LogFileForm(instance=log_file)
        return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form, "log_file_id": log_file_id, "is_edit": True})
    
    def post(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        form = LogFileForm(request.POST, instance=log_file)
        if not form.is_valid():
            return render(request, template_name="logs/log-files/log-file-form.html", context={"form": form, "is_edit": True})
        form.save()
        return render(request, template_name="success.html", context={"message": "Вы успеншо изменили лог-файл!"})


class LogFileDeleteView(views.View):
    def get(self, request, log_file_id, *args, **kwargs):
        log_file = get_object_or_404(LogFile, id=log_file_id)
        log_file.delete()
        return render(request, template_name="success.html", context={"message": "Вы успеншо удалили лог-файл!"})


# Log Type Views


class LogTypeListView(views.View):
    def get(self, request, *args, **kwargs):
        log_types = LogType.objects.all()
        return render(request, template_name="logs/log-types/log-types-list.html", context={"log_types": log_types})
    

class LogTypeAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = LogTypeForm()
        return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = LogTypeForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form})
        LogType.objects.create(**form.cleaned_data)
        return render(request, template_name="success.html", context={"message": "Вы успеншо добавили протокол / ПО!"})


class LogTypeDetailView(views.View):
    def get(self, request, log_type_id, *args, **kwargs):
        log_type = LogType.objects.all(id=log_type_id)
        return render(request, template_name="logs/log-types/log-type-detail.html", context={"log_type": log_type})


class LogTypeEditView(views.View):
    def get(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        form = LogTypeForm(instance=log_type)
        return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form, "log_type_id": log_type_id, "is_edit": True})
    
    def post(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        form = LogTypeForm(request.POST, instance=log_type)
        if not form.is_valid():
            return render(request, template_name="logs/log-types/log-type-form.html", context={"form": form, "is_edit": True})
        form.save()
        return render(request, template_name="success.html", context={"message": "Вы успеншо изменили протокол / ПО!"})


class LogTypeDeleteView(views.View):
    def get(self, request, log_type_id, *args, **kwargs):
        log_type = get_object_or_404(LogType, id=log_type_id)
        log_type.delete()
        return render(request, template_name="success.html", context={"message": "Вы успеншо удалили протокол / ПО!"})