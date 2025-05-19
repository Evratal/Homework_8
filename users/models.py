from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from course.models import Course, Lesson


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Телефон",
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )

    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(upload_to="users/avatars/%Y/%m/%d/", blank=True, null=True, verbose_name="Аватар")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс"
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты"
    )
    payment_link = models.URLField(
        verbose_name="Ссылка на оплату",
        max_length=500,
        blank=True,
        null=True
    )
    stripe_session_id = models.CharField(
        verbose_name="ID сессии Stripe",
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(paid_course__isnull=False) | models.Q(paid_lesson__isnull=False),
                name="payment_has_course_or_lesson"
            )
        ]

    def __str__(self):
        return f"Платёж #{self.id} ({self.user.email})"

    def __str__(self):
        return f"Платёж #{self.id} ({self.user.email})"


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        'course.Course',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'

