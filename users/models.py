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
    def __str__(self):
        return self.username
