from rest_framework import serializers
from .models import Card, User
from .constants import CATEGORY_CHOICES

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
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Card
        fields = ['id', 'title', 'image', 'description', 'budget',
                  'category', 'urls', 'created_at', 'user']
        read_only_fields = ['created_at']

    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title не может быть пустым.")
        return value