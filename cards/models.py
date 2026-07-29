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
