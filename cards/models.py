from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.base_user import BaseUserManager

#  Менеджер для модели User (обязателен для createsuperuser и админки)
class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Логин обязателен')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, **extra_fields)

    def get_by_natural_key(self, login):
        return self.get(**{self.model.USERNAME_FIELD: login})

#  Модель пользователя
class User(models.Model):
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)

    # Поля для админки и прав
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    objects = UserManager()  # теперь менеджер определён

    # Свойства для совместимости с Django
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def get_username(self):
        return self.login

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    # Методы, необходимые для админки и проверки прав
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.login

#  Модель карточки
class Card(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    urls = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')

    def __str__(self):
        return self.title
