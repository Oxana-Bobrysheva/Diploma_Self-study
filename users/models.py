from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# Custom User Manager to handle email-based superuser creation
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    name = models.CharField(
        max_length=100,
        verbose_name="Имя",
        help_text="Укажите своё имя",
        default="Test",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Почта",
        help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите номер телефона",
        validators=[
            RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Номер телефона в формате: '+799999999'. До 15 цифр.")]
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите место проживания"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар"
    )
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="Роль",
        help_text="Выберите роль пользователя"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Пусто, так как username не required при регистрации

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        return self.email

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("card", "картой"),
        ("to_account", "переводом на счёт"),
    ]

    STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("completed", "Оплачено"),
        ("failed", "Не удалось"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="payments",
    )
    payment_date = models.DateField(  # Исправлено: models.DateField
        verbose_name="Дата платежа",
        null=True,
        blank=True,
        help_text="Укажите дату оплаты",
    )
    paid_course = models.ForeignKey(
        "lms.Course",  # Исправлено: обратно на "lms"
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
        help_text="Укажите оплаченный курс",
    )
    paid_material = models.ForeignKey(
        "lms.Material",  # Исправлено: обратно на "lms"
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок",
        help_text="Укажите оплаченный урок",
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Сумма платежа",
        help_text="Укажите сумму платежа",
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
        null=True,
        blank=True,
    )
    status = models.CharField(  # Добавлено: для отслеживания статуса платежа
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус платежа",
        help_text="Текущий статус оплаты",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Stripe Session ID"
    )
    stripe_payment_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Статус оплаты в Stripe"
    )
    payment_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Ссылка на оплату"
    )
    created_at = models.DateTimeField(  # Добавлено: для логирования времени создания платежа
        auto_now_add=True,
        verbose_name="Дата создания платежа"
    )

    def __str__(self):
        course_or_material = self.paid_course if self.paid_course else self.paid_material  # Исправлено: paid_matelial -> paid_material
        return (
            f"Пользователь {self.user} оплатил "
            f"{self.payment_amount} {self.get_payment_type_display()} "
            f"за {course_or_material}. Статус: {self.get_status_display()}"
        )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]  # Новые платежи сверху

class Subscription(models.Model):
    user_sub = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки")

    class Meta:
        unique_together = ("user_sub", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user_sub} подписан на {self.course}"

    test