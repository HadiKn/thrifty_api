from rest_framework.permissions import BasePermission
from .models import Auction, Item, Request


# ✅ هل المستخدم هو صاحب العنصر
class IsItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


# ✅ هل المستخدم ليس صاحب العنصر (للمزايدة / الطلب / claim)
class IsNotItemOwner(BasePermission):
    def has_permission(self, request, view):
        item_id = request.data.get("item")

        if not item_id:
            return False

        item = Item.objects.filter(id=item_id).first()
        return item and item.owner != request.user


# ✅ هل المستخدم هو صاحب المزاد
class IsAuctionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.owner == request.user


# ✅ منع صاحب العنصر من المزايدة
class IsNotAuctionOwner(BasePermission):
    def has_permission(self, request, view):
        auction_id = request.data.get("auction")

        if not auction_id:
            return False

        auction = Auction.objects.filter(id=auction_id).first()
        return auction and auction.item.owner != request.user


# ✅ عرض الطلب فقط لصاحبه أو صاحب العنصر
class IsRequestOwnerOrItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.requester == request.user or
            obj.item.owner == request.user
        )


# ✅ حذف الطلب فقط من صاحبه
class IsRequestOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.requester == request.user


# ✅ فقط صاحب العنصر يستطيع قبول / رفض الطلب
class IsItemOwnerForRequest(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.item.owner == request.user


# ✅ Claim: فقط المشتري أو صاحب العنصر يراه
class IsClaimViewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.buyer == request.user or
            obj.item.owner == request.user
        )