from django.db import models
from users.models import User
from categories.models import Category
from cloudinary.models import CloudinaryField

class Item(models.Model):
    class ListingType(models.TextChoices):
        FIXED_PRICE = 'fixed_price','Fixed Price'
        DONATION = 'donation','Donation'
        AUCTION = 'auction','Auction'

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    listing_type = models.CharField(max_length=20, choices=ListingType.choices, default=ListingType.FIXED_PRICE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('images', folder='items/images/')

    def __str__(self):
        return f"{self.item.name} - {self.image.url}"

class Auction(models.Model):
    class AuctionStatus(models.TextChoices):
        ACTIVE = 'active','Active'
        ENDED = 'ended','Ended'
        CANCELLED = 'cancelled','Cancelled'
        PENDING = 'pending','Pending'
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='auction')
    status = models.CharField(max_length=20, choices=AuctionStatus.choices, default=AuctionStatus.PENDING)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='auctions_won', null=True, blank=True)
    def __str__(self):
        return f"{self.item.name} - {self.current_price}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.bidder.username} - {self.bid_amount}"

