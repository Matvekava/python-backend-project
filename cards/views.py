from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Card, User
from .serializers import CardSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .pagination import CardPagination

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all().order_by('-created_at')
    serializer_class = CardSerializer
    pagination_class = CardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)

        if search:
            queryset = queryset.filter(title__icontains=search)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("Вы не можете редактировать эту карточку.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить эту карточку.")
        instance.delete()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .serializers import FileUploadSerializer
from django.conf import settings

class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]   # или AllowAny, но лучше авторизация

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']

        # Проверка типа файла (только изображения)
        content_type = uploaded_file.content_type
        if not content_type.startswith('image/'):
            return Response(
                {"error": "Файл должен быть изображением."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка расширения (дополнительная защита)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in allowed_extensions:
            return Response(
                {"error": f"Недопустимый формат. Разрешены: {', '.join(allowed_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ограничение размера файла (например, 5 МБ)
        if uploaded_file.size > 5 * 1024 * 1024:
            return Response(
                {"error": "Размер файла не должен превышать 5 МБ."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Генерируем уникальное имя файла (чтобы не было коллизий)
        # Можно сохранить в подпапку uploads/
        filename = default_storage.save(
            os.path.join('uploads', uploaded_file.name),  # сохранит в media/uploads/имя_файла
            ContentFile(uploaded_file.read())
        )

        # Формируем полный URL для доступа к файлу
        file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

        return Response(
            {"url": file_url},
            status=status.HTTP_201_CREATED
        )