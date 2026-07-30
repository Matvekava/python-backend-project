from django.contrib import admin
from .models import User, Card

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'login', 'password')
    search_fields = ('login',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'budget', 'user', 'created_at')
    list_filter = ('category', 'user')
    search_fields = ('title', 'description')