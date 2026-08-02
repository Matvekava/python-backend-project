from rest_framework import serializers
from .models import Card, User
from .constants import CATEGORY_CHOICES
from rest_framework_simplejwt.tokens import RefreshToken

class CardSerializer(serializers.ModelSerializer):
    urls = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0
    )
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    user = serializers.PrimaryKeyRelatedField(read_only=True)   # изменено

    class Meta:
        model = Card
        fields = ['id', 'title', 'image', 'description', 'budget',
                  'category', 'urls', 'created_at', 'user']
        read_only_fields = ['created_at', 'user']   # добавлен 'user'

    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title не может быть пустым.")
        return value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'login', 'password']

    def create(self, validated_data):
        user = User(login=validated_data['login'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class CustomTokenObtainPairSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if not login or not password:
            raise serializers.ValidationError("Требуется login и пароль")

        user = User.objects.filter(login=login).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Неверные учётные данные")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()