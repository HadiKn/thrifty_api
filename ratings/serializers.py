from rest_framework import serializers
from users.serializers import UserMiniSerializer
from .models import SellerRating

class SellerRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating a seller rating"""
    
    class Meta:
        model = SellerRating
        fields = ['rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class SellerRatingListSerializer(serializers.ModelSerializer):
    """Serializer for listing ratings with nested rater, seller, and item details"""
    rater = UserMiniSerializer(read_only=True)
    seller = UserMiniSerializer(read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_detail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SellerRating
        fields = ['id', 'rater', 'seller', 'item_name', 'item_detail_url', 'rating', 'comment', 'created_at']
    
    def get_item_detail_url(self, obj):
        from rest_framework.reverse import reverse
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('item-detail', kwargs={'pk': obj.item.id})
            )
        return None
