from rest_framework.permissions import BasePermission
from .models import Auction, Item, Request


# check item ownership
class IsItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsNotItemOwner(BasePermission):
    def has_permission(self, request, view):
        item_id = request.data.get("item")

        if not item_id:
            return False

        item = Item.objects.filter(id=item_id).first()
        return item and item.owner != request.user


# check auction ownership
class IsAuctionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.owner == request.user


class IsNotAuctionOwner(BasePermission):
    def has_permission(self, request, view):
        auction_id = request.data.get("auction")

        if not auction_id:
            return False

        auction = Auction.objects.filter(id=auction_id).first()
        return auction and auction.item.owner != request.user


class IsRequestOwnerOrItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.requester == request.user or
            obj.item.owner == request.user
        )


class IsRequestOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.requester == request.user


class IsItemOwnerForRequest(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.owner == request.user


class IsClaimViewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.buyer == request.user or
            obj.item.owner == request.user
        )