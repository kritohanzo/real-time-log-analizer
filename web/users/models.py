from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import UserManager as DjangoUserManager
from enum import Enum
from django.core.mail import send_mail


class RoleChoices(Enum):
    VIEWER = "Зритель"
    SPECIALIST = "Специалист"
    ADMIN = "Администратор"

    @classmethod
    def choices(cls):
        return tuple((role.name, role.value) for role in cls)


class UserManager(DjangoUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "VIEWER")
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(
        self, username, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("role") != "ADMIN":
            raise ValueError("Администратор должен иметь роль 'ADMIN'")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    """Модель пользователя."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="Логин",
        max_length=64,
        unique=True,
        validators=[username_validator],
    )
    name = models.CharField(
        verbose_name="Имя", max_length=64, null=True, blank=True
    )
    surname = models.CharField(
        verbose_name="Фамилия", max_length=64, null=True, blank=True
    )
    patronymic = models.CharField(
        verbose_name="Отчество", max_length=64, null=True, blank=True
    )
    email = models.EmailField(
        verbose_name="Электронная почта", max_length=64, null=True, blank=True,
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона", max_length=12, blank=True
    )
    role = models.CharField(
        verbose_name="Роль пользователя",
        max_length=64,
        choices=RoleChoices.choices(),
        default=RoleChoices.VIEWER.name,
        blank=True,
    )
    is_active = models.BooleanField(verbose_name="Активен", default=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "surname", "patronymic", "email"]
    EMAIL_FIELD = "email"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.name, self.surname)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
        ordering = ("role", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_username_email"
            )
        ]

    def __str__(self):
        return self.username
