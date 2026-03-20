from django.urls import path
from .views import ItemListView,ItemRetrieveView
urlpatterns = [
   
    path('list/', ItemListView.as_view(), name='list'),
    path('retrieve/<int:pk>/', ItemRetrieveView.as_view(), name='item'),



]