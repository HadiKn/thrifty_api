from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    detail_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','profile_picture','profile_picture_url','detail_url','average_rating','rating_count')
        read_only_fields = ['profile_picture_url','detail_url','average_rating','rating_count']
        extra_kwargs = {
        'profile_picture': {'write_only': True}
        }
        
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return "https://res.cloudinary.com/dswjejbhq/image/upload/v1773359973/photo_2026-03-13_02-57-42_jpy55s.jpg"

    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('profile', kwargs={'pk': obj.pk})
            )
        return None
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserMiniSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField() 
    detail_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture_url', 'detail_url']
        read_only_fields = fields

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return "https://res.cloudinary.com/dswjejbhq/image/upload/v1773359973/photo_2026-03-13_02-57-42_jpy55s.jpg"
    
    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('profile', kwargs={'pk': obj.pk})
            )
        return None