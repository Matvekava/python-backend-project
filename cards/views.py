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
