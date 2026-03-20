from unicodedata import category
from rest_framework import serializers
from .models import Item, ItemImage, Auction, Bid
from rest_framework.reverse import reverse
from django.utils import timezone
from users.serializers import UserMiniSerializer
from categories.serializers import CategoryMiniSerializer



class ItemListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing items.
    """

    detail_url = serializers.SerializerMethodField()
    category = CategoryMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)
    class Meta:
        model = Item
        fields = ["id", "name", "listing_type", "price", "category", "owner", "created_at","detail_url"]
        read_only_fields = fields
    def get_detail_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('item', kwargs={'pk': obj.pk})
            )
        return None


class ItemSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)
    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "owner",
            "category",
            "description",
            "listing_type",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def validate(self, attrs):
        listing_type = attrs.get("listing_type", getattr(self.instance, "listing_type", None))
        price = attrs.get("price", getattr(self.instance, "price", None))

        if listing_type == Item.ListingType.FIXED_PRICE:
            if price is None:
                raise serializers.ValidationError({"price": "Price is required for fixed price items."})
            if price <= 0:
                raise serializers.ValidationError({"price": "Price must be greater than 0."})
        elif listing_type in (Item.ListingType.DONATION, Item.ListingType.AUCTION):
            if price is not None:
                raise serializers.ValidationError({"price": "Price must be empty for donation or auction items."})

        return attrs


class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image']


class AuctionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing auctions.
    """

    class Meta:
        model = Auction
        fields = ["id", "item", "status", "current_price", "end_time"]
        read_only_fields = fields


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ["id", "item", "status", "start_price", "current_price", "start_time", "end_time", "winner"]
        read_only_fields = ["winner", "status", "current_price"]

    def validate(self, attrs):
        item = attrs.get("item", getattr(self.instance, "item", None))
        start_price = attrs.get("start_price", getattr(self.instance, "start_price", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))

        if item is None:
            raise serializers.ValidationError({"item": "Item is required."})

        if item.listing_type != Item.ListingType.AUCTION:
            raise serializers.ValidationError({"item": "Item must have listing_type=AUCTION to create an auction."})

        if start_price is None:
            raise serializers.ValidationError({"start_price": "Start price is required."})
        if start_price <= 0:
            raise serializers.ValidationError({"start_price": "Start price must be greater than 0."})

        if end_time is None:
            raise serializers.ValidationError({"end_time": "End time is required."})
        if end_time <= timezone.now():
            raise serializers.ValidationError({"end_time": "End time must be in the future."})

        return attrs

    def create(self, validated_data):
        validated_data["current_price"] = validated_data["start_price"]
        return super().create(validated_data)

class BidListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing bids.
    """

    class Meta:
        model = Bid
        fields = ["id", "auction", "bidder", "bid_amount", "bid_date"]
        read_only_fields = fields


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ["id", "auction", "bidder", "bid_amount", "bid_date"]
        read_only_fields = ["id", "bidder", "bid_date"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to place a bid.")

        auction = attrs.get("auction", getattr(self.instance, "auction", None))
        bid_amount = attrs.get("bid_amount", getattr(self.instance, "bid_amount", None))

        if auction is None:
            raise serializers.ValidationError({"auction": "Auction is required."})

        if auction.status != Auction.AuctionStatus.ACTIVE:
            raise serializers.ValidationError({"auction": "You can only bid on an active auction."})

        if timezone.now() >= auction.end_time:
            raise serializers.ValidationError({"auction": "This auction has ended."})

        if auction.item.owner_id == request.user.id:
            raise serializers.ValidationError({"bid_amount": "You cannot bid on your own item."})

        if bid_amount is None:
            raise serializers.ValidationError({"bid_amount": "Bid amount is required."})
        if bid_amount <= 0:
            raise serializers.ValidationError({"bid_amount": "Bid amount must be greater than 0."})

        current_price = auction.current_price if auction.current_price is not None else auction.start_price
        if bid_amount <= current_price:
            raise serializers.ValidationError({"bid_amount": "Bid amount must be higher than the current price."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["bidder"] = request.user
        return super().create(validated_data)

