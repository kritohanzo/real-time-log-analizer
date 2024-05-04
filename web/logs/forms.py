from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import User, RoleChoices
from logs.models import LogType, LogFile, SearchPattern, SearchPatternTypeChoices


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
        empty_label="Выберите тип протокола / ПО"
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