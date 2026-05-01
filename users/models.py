from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
    regex=r'^[\w.@+ \-]+$',
    message='Username may contain letters, digits, spaces, and @/./+/-/_ characters.',
    code='invalid_username'
)]
    )
    email = models.EmailField(unique=True)
    profile_picture = CloudinaryField(
        'profile_pictures/',
        folder='users/profile_pictures/',
        null=True,
        blank=True
    )
    average_rating = models.FloatField(
        default=0.0,
        editable=False,
        help_text="Average rating from all received seller ratings"
    )
    rating_count = models.IntegerField(
        default=0,
        editable=False,
        help_text="Total number of received seller ratings"
    )
    
    def update_average_rating(self):
        """Update average rating and count based on all received ratings"""
        from ratings.models import SellerRating
        ratings = SellerRating.objects.filter(seller=self)
        if ratings.exists():
            from django.db.models import Avg
            avg = ratings.aggregate(average=Avg('rating'))['average']
            self.average_rating = round(avg, 2)
            self.rating_count = ratings.count()
        else:
            self.average_rating = 0.0
            self.rating_count = 0
        self.save(update_fields=['average_rating', 'rating_count'])
    
    def __str__(self):
        return self.username
