from rest_framework import serializers
from categories.serializers import CategorySerializer
from .models import FavoriteCategory

class FavoriteCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding a category to favorites"""
    
    class Meta:
        model = FavoriteCategory
        fields = ['category']
    
    def validate_category(self, value):
        user = self.context['request'].user
        if FavoriteCategory.objects.filter(user=user, category=value).exists():
            raise serializers.ValidationError("This category is already in your favorites.")
        return value

class FavoriteCategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing user's favorite categories"""
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = FavoriteCategory
        fields = ['id', 'category', 'created_at']
