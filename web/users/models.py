from enum import Enum

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from logs.models import NotificationType


class RoleChoices(Enum):
    VIEWER = "Наблюдатель"
    SPECIALIST = "Специалист"
    ADMIN = "Администратор"

    @classmethod
    def choices(cls):
        return tuple((role.name, role.value) for role in cls)


class UserManager(DjangoUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "VIEWER")
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
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
    name = models.CharField(verbose_name="Имя", max_length=64, null=True, blank=True)
    surname = models.CharField(
        verbose_name="Фамилия", max_length=64, null=True, blank=True
    )
    patronymic = models.CharField(
        verbose_name="Отчество", max_length=64, null=True, blank=True
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=64,
        null=True,
        blank=True,
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
    notification_types = models.ManyToManyField(
        NotificationType,
        through="UserNotificationType",
        related_name="users",
        verbose_name="Типы оповещений",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

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


class UserNotificationType(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь, получающий оповещения",
        null=True,
        on_delete=models.SET_NULL,
        related_name="user_notification_types",
    )
    notification_type = models.ForeignKey(
        NotificationType,
        verbose_name="Тип оповещения, которые получает пользователь",
        null=True,
        on_delete=models.SET_NULL,
        related_name="notification_type_users",
    )
