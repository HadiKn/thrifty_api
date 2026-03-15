from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    CategoryAdminListCreateView,
    CategoryAdminRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('list/', CategoryListView.as_view(), name='category-list'),
    path('retrieve/<int:pk>/', CategoryDetailView.as_view(), name='category-retrieve'),

    path('admin/', CategoryAdminListCreateView.as_view(), name='category-admin-list-create'),
    path('admin/<int:pk>/', CategoryAdminRetrieveUpdateDestroyView.as_view(), name='category-admin-modify'),
]