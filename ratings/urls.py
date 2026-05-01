from django.urls import path
from . import views

urlpatterns = [
    # Rate seller from claimed item
    path('item/<int:item_id>/', views.rate_seller_from_item, name='rate-seller-from-item'),
    
    # List views
    path('my-given-ratings/', views.MyGivenRatingsListView.as_view(), name='my-given-ratings'),
    path('my-received-ratings/', views.MyRecievedRatingsListView.as_view(), name='my-received-ratings'),
    path('seller/<int:seller_id>/ratings/', views.SellerRatingsListView.as_view(), name='seller-ratings'),
    
    # Update/Delete ratings
    path('<int:pk>/update/', views.RatingUpdateView.as_view(), name='rating-update'),
    path('<int:pk>/delete/', views.RatingDestroyView.as_view(), name='rating-delete'),
]
