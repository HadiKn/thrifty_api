from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .models import Report
from .serializers import ReportCreateSerializer, ReportSerializer


class ReportCreateView(generics.CreateAPIView):
    """Create a new report"""
    serializer_class = ReportCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ReportListView(generics.ListAPIView):
    """List reports - users see their own reports, admins can see all reports"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Report.objects.all()
        else:
            queryset = Report.objects.filter(reporter=self.request.user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class ReportDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a specific report - users can view their own reports but only admins can update"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(reporter=self.request.user)
    
    def perform_update(self, serializer):
        # Only admins can update reports
        if not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can update reports.")
        
        new_status = serializer.validated_data.get('status')
        if new_status in [Report.ReportStatus.RESOLVED, Report.ReportStatus.DISMISSED]:
            from django.utils import timezone
            serializer.save(resolved_at=timezone.now())
        else:
            serializer.save()
