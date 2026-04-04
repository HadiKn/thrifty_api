from django.utils import timezone
from rest_framework import serializers
from .models import Item, ItemImage, Auction, Bid, Claim, Request
from users.models import User
import pytz
from rest_framework.reverse import reverse
from users.serializers import UserMiniSerializer
from categories.serializers import CategoryMiniSerializer, CategorySerializer
from categories.models import Category
from django.db import transaction


class BaseItemSerializer(serializers.ModelSerializer):

    def get_request(self):
        return self.context.get("request")

    def get_user(self):
        request = self.get_request()
        return request.user if request else None

    def build_url(self, obj, view_name):
        request = self.get_request()
        if request:
            return request.build_absolute_uri(
                reverse(view_name, kwargs={'pk': obj.pk})
            )
        return None


class ItemListSerializer(BaseItemSerializer):
    """Lightweight serializer for list and retrieve views"""
    detail_url = serializers.SerializerMethodField()
    category = CategoryMiniSerializer(read_only=True)
    owner = UserMiniSerializer(read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "listing_type",
            "price",
            "category",
            "owner",
            "description",
            "is_available",
            "created_at",
            "updated_at",
            "detail_url"
        ]
        read_only_fields = fields

    def get_detail_url(self, obj):
        return self.build_url(obj, 'item-detail')


class ItemSerializer(BaseItemSerializer):
    """Serializer for create, update, delete operations"""
    owner = UserMiniSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

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
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at", "is_available"]

    def get_detail_url(self, obj):
        return self.build_url(obj, 'item-detail')

    def validate(self, attrs):
        listing_type = attrs.get(
            "listing_type",
            getattr(self.instance, "listing_type", None)
        )

        price = attrs.get(
            "price",
            getattr(self.instance, "price", None)
        )

        if listing_type == Item.ListingType.FIXED_PRICE:
            if price is None:
                raise serializers.ValidationError({"price": "Price is required."})
            if price <= 0:
                raise serializers.ValidationError({"price": "Price must be > 0."})

        elif listing_type in (Item.ListingType.DONATION, Item.ListingType.AUCTION):
            if price is not None:
                raise serializers.ValidationError({"price": "Price must be empty."})

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


# serializers.py

from rest_framework import serializers
from django.utils import timezone
from .models import Auction, Item


class AuctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auction
        fields = [
            "id",
            "item",
            "status",
            "start_price",
            "current_price",
            "start_time",
            "end_time",
            "winner",
        ]
        read_only_fields = ["winner", "status", "current_price", "start_time"]

    def validate(self, attrs):
        item = attrs.get("item", getattr(self.instance, "item", None))
        start_price = attrs.get("start_price", getattr(self.instance, "start_price", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))

        if item is None:
            raise serializers.ValidationError({"item": "Item is required."})

        if item.listing_type != Item.ListingType.AUCTION:
            raise serializers.ValidationError({
                "item": "Item must have listing_type=AUCTION to create an auction."
            })

        if start_price is None:
            raise serializers.ValidationError({"start_price": "Start price is required."})

        if start_price <= 0:
            raise serializers.ValidationError({"start_price": "Start price must be greater than 0."})

        if end_time is None:
            raise serializers.ValidationError({"end_time": "End time is required."})

        # ✅ Handle naive datetime safely
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time)

        # ✅ Validate using Django's timezone
        if end_time <= timezone.now():
            raise serializers.ValidationError({
                "end_time": "End time must be in the future."
            })

        attrs["end_time"] = end_time
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

        # WALLET INTEGRATION: Check bidder's wallet balance
        from wallet.services import WalletService
        bidder_wallet = WalletService.get_or_create_wallet(request.user)
        
        if bidder_wallet.balance < bid_amount:
            raise serializers.ValidationError({"bid_amount": f"Insufficient wallet balance. Your balance: {bidder_wallet.balance}, Required: {bid_amount}"})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["bidder"] = request.user
        return super().create(validated_data)


class ItemPurchaseSerializer(serializers.Serializer):
    """Serializer for purchasing fixed-price items"""
    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        return attrs


class ClaimSerializer(serializers.ModelSerializer):
    buyer = UserMiniSerializer(read_only=True)

    class Meta:
        model = Claim
        fields = [
            "id",
            "item",
            "buyer",
            "claimed_at",
        ]
        read_only_fields = ["buyer", "claimed_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        item = attrs.get("item")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        if not item.is_available:
            raise serializers.ValidationError("Item is not available.")

        if hasattr(item, "claim"):
            raise serializers.ValidationError("Item already claimed.")

        if item.owner == request.user:
            raise serializers.ValidationError("You cannot claim your own item.")

        if item.listing_type == Item.ListingType.AUCTION:
            raise serializers.ValidationError("Auction items cannot be claimed directly.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        item = validated_data["item"]
        validated_data["buyer"] = request.user
        claim = super().create(validated_data)
        return claim


class BaseRequestSerializer(serializers.ModelSerializer):

    def get_request(self):
        return self.context.get("request")

    def get_user(self):
        request = self.get_request()
        return request.user if request else None

    def validate_auth(self):
        request = self.get_request()
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        return request.user


class RequestCreateSerializer(BaseRequestSerializer):

    requester = UserMiniSerializer(read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "item",
            "requester",
            "status",
            "created_at",
        ]
        read_only_fields = ["requester", "created_at", "status"]

    def validate(self, attrs):
        user = self.validate_auth()
        item = attrs.get("item")

        # Only allow requests for donation items
        if item.listing_type != Item.ListingType.DONATION:
            raise serializers.ValidationError("Requests are only allowed for donation items.")

        if Request.objects.filter(
            item=item,
            requester=user
        ).exists():
            raise serializers.ValidationError("You already requested this item.")

        if item.owner == user:
            raise serializers.ValidationError("You cannot request your own item.")

        if not item.is_available:
            raise serializers.ValidationError("Item is not available.")

        return attrs

    def create(self, validated_data):
        validated_data["requester"] = self.get_user()
        return super().create(validated_data)


class RequestActionSerializer(BaseRequestSerializer):

    requester = UserMiniSerializer(read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "requester",
            "status",
            "created_at",
        ]
        read_only_fields = ["item", "requester", "created_at"]

    def validate(self, attrs):
        user = self.validate_auth()
        new_status = attrs.get("status")

        if not self.instance:
            raise serializers.ValidationError("Invalid request instance.")

        request_obj = self.instance
        item = request_obj.item

        if item.owner != user:
            raise serializers.ValidationError("You do not have permission to perform this action.")

        if request_obj.status != Request.RequestStatus.PENDING:
            raise serializers.ValidationError("This request has already been processed.")

        if new_status not in [
            Request.RequestStatus.ACCEPTED,
            Request.RequestStatus.REJECTED
        ]:
            raise serializers.ValidationError("Invalid status.")

        if new_status == Request.RequestStatus.ACCEPTED:
            if not item.is_available:
                raise serializers.ValidationError("Item is already not available.")
            if Claim.objects.filter(item=item).exists():
                raise serializers.ValidationError("This item is already claimed.")

        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            new_status = validated_data.get("status")
            item = instance.item

            if new_status == Request.RequestStatus.ACCEPTED:
                if Claim.objects.filter(item=item).exists():
                    raise serializers.ValidationError("This item is already claimed.")

            instance.status = new_status
            instance.save()

            if new_status == Request.RequestStatus.ACCEPTED:
                item.is_available = False
                item.save()

                Claim.objects.create(
                    item=item,
                    buyer=instance.requester
                )

                Request.objects.filter(
                    item=item,
                    status=Request.RequestStatus.PENDING
                ).exclude(id=instance.id).update(
                    status=Request.RequestStatus.REJECTED
                )

        return instance


class RequestSerializer(BaseRequestSerializer):
    requester = UserMiniSerializer(read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "item",
            "requester",
            "status",
            "created_at",
        ]
        read_only_fields = ["requester", "created_at"]

    def validate(self, attrs):
        user = self.validate_auth()
        item = attrs.get("item")

        if Request.objects.filter(
            item=item,
            requester=user
        ).exists():
            raise serializers.ValidationError("You already requested this item.")

        if item.owner == user:
            raise serializers.ValidationError("You cannot request your own item.")

        if not item.is_available:
            raise serializers.ValidationError("Item is not available.")

        return attrs

    def create(self, validated_data):
        validated_data["requester"] = self.get_user()
        return super().create(validated_data)