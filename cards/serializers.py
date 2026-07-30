from rest_framework import serializers
from .models import Card, User

class CardSerializer(serializers.ModelSerializer):
    urls = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Card
        fields = ['id', 'title', 'image', 'description', 'budget',
                  'category', 'urls', 'created_at', 'user']
        read_only_fields = ['created_at']