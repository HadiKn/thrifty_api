from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import schema
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .models import SellerRating
from .serializers import (
    SellerRatingCreateSerializer, 
    SellerRatingListSerializer
)
from items.models import Item, Claim

@extend_schema(
    summary="Rate seller from claimed item",
    description="Rate a seller after successfully claiming an item. Only users who have claimed the item can rate the seller.",
    request=SellerRatingCreateSerializer,
    responses={
        201: {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                'comment': {'type': 'string', 'nullable': True},
                'created_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    },
    tags=['Ratings']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_seller_from_item(request, item_id):
    """Rate a seller from a claimed item"""
    item = get_object_or_404(Item, id=item_id)
    
    # Check if user has claimed this item
    if not Claim.objects.filter(buyer=request.user, item=item).exists():
        return Response(
            {"error": "You can only rate sellers for items you've claimed"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cannot rate your own items
    if item.owner == request.user:
        return Response(
            {"error": "You cannot rate your own items"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already rated
    if SellerRating.objects.filter(rater=request.user, item=item).exists():
        return Response(
            {"error": "You have already rated this item's seller"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = SellerRatingCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Create rating
        rating = serializer.save(
            rater=request.user, 
            seller=item.owner,
            item=item
        )
        
        # Update seller's average rating and count
        item.owner.update_average_rating()
        
        return Response({
            'id': rating.id,
            'rating': rating.rating,
            'comment': rating.comment,
            'created_at': rating.created_at
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyGivenRatingsListView(generics.ListAPIView):
    """List all ratings given by current user"""
    serializer_class = SellerRatingListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SellerRating.objects.filter(rater=self.request.user)

class MyRecievedRatingsListView(generics.ListAPIView):
    """List all ratings recieved to current user"""
    serializer_class = SellerRatingListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SellerRating.objects.filter(seller=self.request.user)

class SellerRatingsListView(generics.ListAPIView):
    """List all ratings received by a seller"""
    serializer_class = SellerRatingListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return SellerRating.objects.filter(seller_id=seller_id)

class RatingUpdateView(generics.UpdateAPIView):
    """Update an existing rating"""
    serializer_class = SellerRatingCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SellerRating.objects.filter(rater=self.request.user)
    
    def perform_update(self, serializer):
        rating = serializer.save()
        rating.seller.update_average_rating()

class RatingDestroyView(generics.DestroyAPIView):
    """Delete a rating"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SellerRating.objects.filter(rater=self.request.user)
    
    def perform_destroy(self, instance):
        seller = instance.seller
        instance.delete()
        seller.update_average_rating()
