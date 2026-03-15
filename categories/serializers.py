from rest_framework import serializers
from .models import Category
from rest_framework.reverse import reverse
class CategorySerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent' , 'detail_url']
        read_only_fields = ['detail_url']       
    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('category-retrieve', kwargs={'pk': obj.pk})
            )
        return None