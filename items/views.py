from django.shortcuts import render
from rest_framework import generics
from .serializers import ItemListSerializer,ItemSerializer
from .models import Item

class ItemListView(generics.ListAPIView):
    """
    Endpoint for listing Items using mini serializer with nested serializers for owner and category
    """
    queryset = Item.objects.all()
    serializer_class = ItemListSerializer

class ItemRetrieveView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


