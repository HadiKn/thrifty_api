from django.shortcuts import render
from rest_framework import generics, status, filters, parsers  
from django.contrib.auth import get_user_model
from .serializers import UserSerializer,UserMiniSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

User = get_user_model()

class UserListView(generics.ListAPIView):
    serializer_class = UserMiniSerializer
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    @method_decorator(cache_page(60,key_prefix='list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    this endpoint is for retrieving my personal account + updating my account info using patch or put (like adding a profile picture)
    """
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    def get_object(self):
        return self.request.user

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [AllowAny]
    @extend_schema(
        request=UserSerializer,  # Use the serializer to define the request body schema
        description="Create a new user. Supports form-data, JSON, and multipart uploads, you can use json format then upload a profile picture using the myprofile endpoint",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDestroyView(generics.DestroyAPIView):
    """
    deletes the user sending the request verified by jwt Authorization header
    """
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

