from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.ReportCreateView.as_view(), name='report-create'),
    path('list/', views.ReportListView.as_view(), name='report-list'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
]
