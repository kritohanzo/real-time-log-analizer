from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import User, RoleChoices


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        max_length=64,
        required=True,
        error_messages={"required": "Обязателен"},
        widget=forms.TextInput(
            attrs={"placeholder": "Введите логин", "class": "form-control"}
        ),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )


class CreateUserForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=64,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите логин", "class": "form-control"}
        ),
    )
    name = forms.CharField(
        label="Имя",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите имя", "class": "form-control"}
        ),
    )
    surname = forms.CharField(
        label="Фамилия",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите фамилию", "class": "form-control"}
        ),
    )
    patronymic = forms.CharField(
        label="Отчество",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите отчество", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        label="Почта",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите почту", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )
    role = forms.ChoiceField(
        choices=RoleChoices.choices(),
        label="Роль",
        required=True,
        widget=forms.Select(
            attrs={"placeholder": "Выберите роль", "class": "form-select"}
        ),
    )
