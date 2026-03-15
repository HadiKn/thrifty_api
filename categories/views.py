from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    """
    Public endpoint: list all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Public endpoint: retrieve a single category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"


class CategoryAdminListCreateView(generics.ListCreateAPIView):
    """
    Admin endpoint: list and create categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class CategoryAdminRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin endpoint: retrieve, update, and delete categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "pk"
