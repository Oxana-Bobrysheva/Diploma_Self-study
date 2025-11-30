from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# Custom User Manager to handle email-based superuser creation
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    name = models.CharField(
        max_length=100,
        verbose_name="Имя",
        help_text="Укажите своё имя",
        default="Ученик",
    )
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите номер телефона",
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Номер телефона в формате: '+799999999'. До 15 цифр.",
            )
        ],
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите место проживания",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )
    ROLE_CHOICES = [
        ("student", "Студент"),
        ("teacher", "Преподаватель"),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="student",
        verbose_name="Роль",
        help_text="Выберите роль пользователя",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    object = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        return self.email
