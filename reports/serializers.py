from rest_framework import serializers
from users.serializers import UserMiniSerializer
from items.serializers import ItemListSerializer
from .models import Report

class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reports"""
    
    class Meta:
        model = Report
        fields = ['reported_item', 'reason', 'description']
    

class ReportSerializer(serializers.ModelSerializer):
    """Serializer for listing and admin operations with nested data"""
    reporter = UserMiniSerializer(read_only=True)
    reported_item = ItemListSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reported_item', 'reason',
            'description', 'status', 'admin_notes', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['reporter', 'created_at', 'resolved_at']