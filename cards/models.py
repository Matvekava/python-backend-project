from django.db import models

class Card(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(max_length=500, blank=True)   # ссылка на картинку
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)  # деньги
    category = models.CharField(max_length=100)
    urls = models.JSONField(default=list)                # список строк
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models

class User(models.Model):
    login = models.CharField(max_length=100, unique=True)   # логин уникальный
    password = models.CharField(max_length=100)             # пока просто текст

    def __str__(self):
        return self.login

class Card(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    urls = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,   # или PROTECT – выбираем ниже
        related_name='cards'
    )
