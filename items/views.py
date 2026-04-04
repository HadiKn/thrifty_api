from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Item, ItemImage, Auction, Bid, Request, Claim
from .serializers import (
    ItemListSerializer, ItemImageSerializer, ItemSerializer,
    AuctionSerializer, ClaimSerializer,
    BidListSerializer, AuctionListSerializer,
    BidSerializer, RequestCreateSerializer,
    RequestActionSerializer, RequestSerializer, ItemPurchaseSerializer
)
from .permissions import (
    IsItemOwner,
    IsNotItemOwner,
    IsAuctionOwner,
    IsNotAuctionOwner,
    IsRequestOwnerOrItemOwner,
    IsRequestOwner,
    IsItemOwnerForRequest,
    IsClaimViewer
)

# List all items with filtering support
class ItemListView(generics.ListAPIView):
    """
    Endpoint for listing Items using mini serializer with nested serializers for owner and category
    """
    serializer_class = ItemListSerializer

    def get_queryset(self):
        queryset = Item.objects.all()

        # Filter by availability
        available = self.request.query_params.get('available')
        if available:
            if available.lower() == 'true':
                queryset = queryset.filter(is_available=True)
            elif available.lower() == 'false':
                queryset = queryset.filter(is_available=False)

        # Filter by listing type
        listing_type = self.request.query_params.get('type')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset.order_by('-created_at')


# List images for a specific item
class ItemImagesView(generics.ListAPIView):
    serializer_class = ItemImageSerializer

    def get_queryset(self):
        item_id = self.kwargs.get('pk')
        return ItemImage.objects.filter(item_id=item_id)


# Retrieve single item details
class ItemRetrieveView(generics.RetrieveAPIView):
    serializer_class = ItemListSerializer
    queryset = Item.objects.all()


class ItemAuctionView(generics.RetrieveAPIView):
    """Get auction for a specific item"""
    serializer_class = AuctionSerializer
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        item = get_object_or_404(Item, id=pk)
        
        try:
            return item.auction 
        except Auction.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("No auction found for this item") 


# List all auctions
class AuctionListView(generics.ListAPIView):
    serializer_class = AuctionListSerializer
    queryset = Auction.objects.all().order_by('-id')


# List bids for a specific auction
class AuctionBidsView(generics.ListAPIView):
    serializer_class = BidListSerializer

    def get_queryset(self):
        auction_id = self.kwargs.get('pk')
        return Bid.objects.filter(
            auction_id=auction_id
        ).order_by('-bid_amount')


# List bids by a specific user
class UserBidsView(generics.ListAPIView):
    serializer_class = BidListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        return Bid.objects.filter(
            bidder_id=user_id
        ).order_by('-bid_date')


# View claims for a specific item
class ItemClaimView(generics.RetrieveAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated, IsClaimViewer]

    def get_object(self):
        item_id = self.kwargs.get('pk')
        claim = Claim.objects.get(item_id=item_id)
        self.check_object_permissions(self.request, claim)
        return claim


# List all requests (sent and received)
class RequestListView(generics.ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, IsRequestOwnerOrItemOwner]

    def get_queryset(self):
        user = self.request.user

        # Get filter parameter
        request_type = self.request.query_params.get('type', 'all')

        if request_type == 'sent':
            # Only requests I sent
            return Request.objects.filter(requester=user)
        elif request_type == 'received':
            # Only requests I received
            return Request.objects.filter(item__owner=user)
        else:
            # All requests (default)
            sent_requests = Request.objects.filter(requester=user)
            received_requests = Request.objects.filter(item__owner=user)
            return (sent_requests | received_requests).distinct()


# List items owned by current user
class MyItemsView(generics.ListAPIView):
    serializer_class = ItemListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')


# List items claimed by current user
class MyClaimedItemsView(generics.ListAPIView):
    serializer_class = ItemListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(
            claim__buyer=self.request.user
        ).order_by('-created_at')


# List bids placed by current user
class MyBidsView(generics.ListAPIView):
    serializer_class = BidListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bid.objects.filter(
            bidder=self.request.user
        ).order_by('-bid_date')


# Create new item
class ItemCreateView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Add images to an existing item
class AddItemImagesView(generics.CreateAPIView):
    serializer_class = ItemImageSerializer
    permission_classes = [IsAuthenticated, IsItemOwner]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        item = Item.objects.get(id=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, item)

        serializer.save(
            item=item,
            image=self.request.FILES.get('image')
        )


# Delete single image
class DeleteItemImageView(generics.DestroyAPIView):
    serializer_class = ItemImageSerializer
    permission_classes = [IsAuthenticated, IsItemOwner]
    
    def get_object(self):
        item_id = self.kwargs.get('item_pk')
        image_id = self.kwargs.get('image_pk')
        return get_object_or_404(ItemImage, id=image_id, item_id=item_id)


# Update single image
class UpdateItemImageView(generics.UpdateAPIView):
    serializer_class = ItemImageSerializer
    permission_classes = [IsAuthenticated, IsItemOwner]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        item_id = self.kwargs.get('item_pk')
        image_id = self.kwargs.get('image_pk')
        return get_object_or_404(ItemImage, id=image_id, item_id=item_id)


# Create new auction
class AuctionCreateView(generics.CreateAPIView):
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated, IsItemOwner]

    def perform_create(self, serializer):
        # Auto-start auction when created
        serializer.save(
            status=Auction.AuctionStatus.ACTIVE,
            start_time=timezone.now()
        )


# Create new bid
class BidCreateView(generics.CreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, IsNotAuctionOwner]

    def perform_create(self, serializer):
        # Check wallet balance before allowing bid
        from wallet.services import WalletService
        bidder_wallet = WalletService.get_or_create_wallet(self.request.user)
        bid_amount = serializer.validated_data['bid_amount']
        
        if bidder_wallet.balance < bid_amount:
            raise serializers.ValidationError(
                f"Insufficient wallet balance. Your balance: {bidder_wallet.balance}, Required: {bid_amount}"
            )
        
        # Save bid and update auction current price
        bid = serializer.save(bidder=self.request.user)
        
        # Update auction's current price to this bid amount
        auction = bid.auction
        auction.current_price = bid_amount
        auction.save()
        
        return bid


# Create new request
class RequestCreateView(generics.CreateAPIView):
    serializer_class = RequestCreateSerializer
    permission_classes = [IsAuthenticated, IsNotItemOwner]
    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

# Purchase fixed-price item
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_item(request, item_id):
    """
    Purchase a fixed-price item using wallet
    """
    serializer = ItemPurchaseSerializer(data={}, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get the item
        item = get_object_or_404(Item, id=item_id)
        
        # Validate item is available for purchase
        if item.listing_type != Item.ListingType.FIXED_PRICE:
            return Response(
                {'error': 'This item is not available for direct purchase.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not item.is_available:
            return Response(
                {'error': 'Item is not available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if item.owner == request.user:
            return Response(
                {'error': 'You cannot purchase your own item.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process wallet payment
        from wallet.services import WalletService
        buyer_wallet = WalletService.get_or_create_wallet(request.user)
        seller_wallet = WalletService.get_or_create_wallet(item.owner)
        
        result = WalletService.process_complete_purchase(
            buyer_wallet=buyer_wallet,
            seller_wallet=seller_wallet,
            amount=item.price,
            reference_type='item',
            reference_id=str(item.id),
            description=f'Purchase of {item.name}'
        )
        
        # Mark item as unavailable
        item.is_available = False
        item.save()
        
        # Create claim record
        claim = Claim.objects.create(
            item=item,
            buyer=request.user
        )
        
        return Response({
            'message': 'Purchase successful!',
            'transaction': {
                'buyer_transaction_id': result['buyer_transaction'].id,
                'seller_transaction_id': result['seller_transaction'].id,
                'amount': result['amount']
            },
            'claim_id': claim.id,
            'item': {
                'id': item.id,
                'name': item.name,
                'price': item.price
            }
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Purchase failed. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update existing item
class ItemUpdateView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, IsItemOwner]


# Update existing auction
class AuctionUpdateView(generics.UpdateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated, IsAuctionOwner]


# Update request status (accept/reject)
class RequestActionView(generics.UpdateAPIView):
    serializer_class = RequestActionSerializer
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated, IsItemOwnerForRequest]

    def perform_update(self, serializer):
        serializer.save(status=self.request.data.get("status"))


# Delete item (and related data)
class ItemDeleteView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsItemOwner]

    def perform_destroy(self, instance):
        if not instance.is_available:
            raise PermissionDenied("You cannot delete an unavailable item.")

        # Delete related data
        Request.objects.filter(item=instance).delete()
        
        auction = getattr(instance, 'auction', None)
        if auction:
            Bid.objects.filter(auction=auction).delete()
            auction.delete()

        instance.delete()


# Delete request
class RequestDeleteView(generics.DestroyAPIView):
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated, IsRequestOwner]

    def perform_destroy(self, instance):
        if instance.status != Request.RequestStatus.PENDING:
            raise PermissionDenied("You can only delete a pending request.")
        
        instance.delete()
