from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import User, RoleChoices
from logs.models import LogType, LogFile


class LogFileForm(forms.ModelForm):
    name = forms.CharField(
        label="Имя файла (для простоты понимания)",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите имя файла", "class": "form-control"}
        ),
    )
    path = forms.CharField(
        label="Путь до файла",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите путь до файла", "class": "form-control"}
        ),
    )
    type = forms.ModelChoiceField(
        queryset=LogType.objects.all(),
        label="Тип протокола / ПО",
        required=False,
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="Выберите тип протокола / ПО"
    )
    
    class Meta:
        model = LogFile
        fields = ("name", "path", "type")

class LogTypeForm(forms.ModelForm):
    name = forms.CharField(
        label="Имя протокола / ПО",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите имя протокола / ПО", "class": "form-control"}
        ),
    )
    
    class Meta:
        model = LogType
        fields = ("name",)