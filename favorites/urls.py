from django.urls import path
from . import views

urlpatterns = [
    # List and create favorite categories
    path('categories/', views.FavoriteCategoryListCreateView.as_view(), name='favorite-categories-list-create'),
    
    # Remove favorite category
    path('categories/<int:pk>/', views.FavoriteCategoryDestroyView.as_view(), name='favorite-category-detail'),
    
    # Get recommended categories
    path('recommended-categories/', views.get_recommended_categories, name='recommended-categories'),
]
