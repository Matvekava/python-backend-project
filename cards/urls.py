from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet, UserViewSet
from .views import FileUploadView


router = DefaultRouter()
router.register(r'cards', CardViewSet, basename='card')   # <-- ваш старый роутер
router.register(r'users', UserViewSet, basename='user')   # <-- добавляем новый

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]