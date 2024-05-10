from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import User, RoleChoices
from logs.models import LogType, LogFile, SearchPattern, SearchPatternTypeChoices, AnomalousEvent
import datetime

class LogFileForm(forms.ModelForm):
    name = forms.CharField(
        label="Краткое название или описание лог-файла",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите краткое название или описание лог-файла", "class": "form-control"}
        ),
    )
    path = forms.CharField(
        label="Путь до файла",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите путь до файла", "class": "form-control"}
        ),
    )
    type = forms.ModelChoiceField(
        queryset=LogType.objects.all(),
        label="Тип протокола / ПО",
        required=True,
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="—"
    )
    
    class Meta:
        model = LogFile
        fields = ("name", "path", "type")


class LogTypeForm(forms.ModelForm):
    name = forms.CharField(
        label="Краткое название или описание протокола / ПО",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите краткое название или описание протокола / ПО", "class": "form-control"}
        ),
    )
    search_patterns = forms.ModelMultipleChoiceField(
        queryset=SearchPattern.objects.all(),
        label="Поиксовые паттерны",
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check form-check-inline"}
        ),
    )
    
    class Meta:
        model = LogType
        fields = ("name", "search_patterns")


class SearchPatternForm(forms.ModelForm):
    name = forms.CharField(
        label="Краткое название или описание поискового паттерна",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите краткое название или описание поискового паттерна", "class": "form-control"}
        ),
    )
    pattern = forms.CharField(
        label="Поисковый паттерн",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите поисковый паттерн", "class": "form-control"}
        ),
    )
    search_type = forms.ChoiceField(
        choices=SearchPatternTypeChoices.choices(),
        label="Тип поиска",
        required=True,
        widget=forms.Select(
            attrs={"placeholder": "Выберите тип поиска", "class": "form-select"}
        ),
    )

    class Meta:
        model = SearchPattern
        fields = ("name", "pattern", "search_type")


class MainPageForm(forms.Form):
    start_datetime = forms.DateTimeField(
        label="Начало периода",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Выберите начала периода",
                "class": "form-control",
                "type": "datetime-local",
                "value": datetime.datetime.now().strftime('%Y-%m-%d 00:00')}
        ),
    )
    end_datetime = forms.DateTimeField(
        label="Конец периода",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Выберите начала периода",
                "class": "form-control",
                "type": "datetime-local",
                "value": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00')}
        ),
    )
    log_file = forms.ModelChoiceField(
        queryset=LogFile.objects.all(),
        required=False,
        label="Лог-файл",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="Любой"
    )
    log_type = forms.ModelChoiceField(
        queryset=LogType.objects.all(),
        required=False,
        label="Тип протокола / ПО",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="Любой"
    )
    search_pattern = forms.ModelChoiceField(
        queryset=SearchPattern.objects.all(),
        required=False,
        label="Поисковый паттерн",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="Любой"
    )


class AnomalousEventSearchForm(forms.Form):
    text = forms.CharField(
        label="Текст события",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите текст события", "class": "form-control"}
        ),
    )
    start_datetime = forms.DateTimeField(
        label="Начало периода",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Выберите начала периода",
                "class": "form-control",
                "type": "datetime-local",
                "value": "—"
            }
        ),
    )
    end_datetime = forms.DateTimeField(
        label="Конец периода",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Выберите начала периода",
                "class": "form-control",
                "type": "datetime-local",
                "value": "—"
            }
        ),
    )
    log_file = forms.ModelChoiceField(
        queryset=LogFile.objects.all(),
        required=False,
        label="Лог-файл",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),
        empty_label="Любой"
    )