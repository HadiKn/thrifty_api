from django.urls import path
from .views import UserListView,UserRetrieveView,UserCreateView
urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user_register'),
    path('list/', UserListView.as_view(), name='list'),
    path('retrieve/<int:pk>/', UserRetrieveView.as_view(), name='profile'),


]