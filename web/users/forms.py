from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import User, RoleChoices
from logs.models import NotificationType


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


class UserForm(forms.ModelForm):
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
    phone_number = forms.CharField(
        label="Номер телефона",
        max_length=12,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите номер телефона", "class": "form-control"}
        ),
    ) 
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль"
            },
            render_value=True
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
    notification_types = forms.ModelMultipleChoiceField(
        queryset=NotificationType.objects.all(),
        label="Типы оповещений",
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check form-check-inline"}
        ),
        initial=NotificationType.objects.filter(method="websocket")
    )

    class Meta:
        model = User
        fields = ("username", "name", "surname", "patronymic", "email", "phone_number", "password", "role", "notification_types")
