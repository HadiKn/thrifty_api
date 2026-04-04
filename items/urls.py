from django.urls import path
from .views import (
    ItemListView,
    ItemRetrieveView,
    ItemAuctionView,
    AuctionListView,
    AuctionBidsView,
    UserBidsView,
    ItemClaimView,
    RequestListView,
    MyItemsView,
    MyClaimedItemsView,
    MyBidsView,
    ItemCreateView,
    AddItemImagesView,
    DeleteItemImageView,
    UpdateItemImageView,
    BidCreateView,
    RequestCreateView,
    ItemUpdateView,
    AuctionUpdateView,
    RequestActionView,
    ItemDeleteView,
    RequestDeleteView,
    ItemImagesView,
    AuctionCreateView,
    purchase_item,
)

urlpatterns = [
    # =====================
    # LIST & RETRIEVE
    # =====================
    path('list/', ItemListView.as_view(), name='item-list'),
    path('retrieve/<int:pk>/', ItemRetrieveView.as_view(), name='item-detail'),
    path('<int:pk>/claim/', ItemClaimView.as_view(), name='item-claim'),
    path('requests/', RequestListView.as_view(), name='request-list'),
    path('my-items/', MyItemsView.as_view(), name='my-items'),
    path('my-claims/', MyClaimedItemsView.as_view(), name='my-claims'),
    path('<int:pk>/images/', ItemImagesView.as_view(), name='item-images'),
    path('<int:pk>/auction/', ItemAuctionView.as_view(), name='item-auction'),

    # path('auctions/', AuctionListView.as_view(), name='auction-list'),
    # path('auctions/<int:pk>/', AuctionDetailView.as_view(), name='auction-detail'),
    # path('auctions/<int:pk>/bids/', AuctionBidsView.as_view(), name='auction-bids'),
    # path('users/<int:pk>/bids/', UserBidsView.as_view(), name='user-bids'),
    # path('my-bids/', MyBidsView.as_view(), name='my-bids'),

    # =====================
    # CREATE
    # =====================
    path('create/', ItemCreateView.as_view(), name='item-create'),
    path('<int:pk>/images/', AddItemImagesView.as_view(), name='add-item-images'),
    path('request/create/', RequestCreateView.as_view(), name='request-create'),
    path('<int:item_id>/purchase/', purchase_item, name='item-purchase'),
    path('auctions/create/', AuctionCreateView.as_view(), name='auction-create'),
    path('bids/create/', BidCreateView.as_view(), name='bid-create'),

    # =====================
    # UPDATE
    # =====================
    path('<int:pk>/update/', ItemUpdateView.as_view(), name='item-update'),
    path('requests/<int:pk>/action/', RequestActionView.as_view(), name='request-action'),
    path('<int:item_pk>/images/<int:image_pk>/update/', UpdateItemImageView.as_view(), name='update-item-image'),


    # path('auctions/<int:pk>/update/', AuctionUpdateView.as_view(), name='auction-update'),

    # =====================
    # DELETE
    # =====================
    path('<int:pk>/delete/', ItemDeleteView.as_view(), name='item-delete'),
    path('requests/<int:pk>/delete/', RequestDeleteView.as_view(), name='request-delete'),
    path('<int:item_pk>/images/<int:image_pk>/delete/', DeleteItemImageView.as_view(), name='delete-item-image'),

]