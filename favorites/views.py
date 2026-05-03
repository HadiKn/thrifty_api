from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import FavoriteCategory
from .serializers import FavoriteCategoryCreateSerializer, FavoriteCategoryListSerializer

class FavoriteCategoryListCreateView(generics.ListCreateAPIView):
    """List and create favorite categories for current user"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FavoriteCategoryCreateSerializer
        return FavoriteCategoryListSerializer
    
    def get_queryset(self):
        return FavoriteCategory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteCategoryDestroyView(generics.DestroyAPIView):
    """Remove a category from favorites"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteCategory.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get user's recommended categories",
    description="Get categories based on purchase history and favorites",
    tags=['Favorites']
)
def get_recommended_categories(request):
    """Get recommended categories based on purchase history and favorites"""
    from items.models import Claim
    
    # Categories from purchase history
    purchased_categories = Claim.objects.filter(
        buyer=request.user
    ).values_list('item__category', flat=True).distinct()
    
    # Favorite categories
    favorite_categories = FavoriteCategory.objects.filter(
        user=request.user
    ).values_list('category', flat=True)
    
    # Combine both sources
    recommended_category_ids = set(purchased_categories) | set(favorite_categories)
    
    # Return category details
    from categories.models import Category
    categories = Category.objects.filter(id__in=recommended_category_ids)
    
    from categories.serializers import CategorySerializer
    serializer = CategorySerializer(categories, many=True)
    
    return Response({
        'recommended_categories': serializer.data,
        'total_count': len(recommended_category_ids)
    })
