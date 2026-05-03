from django.db import models
from django.conf import settings
from categories.models import Category

class FavoriteCategory(models.Model):
    """User's favorite categories for personalized recommendations"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_categories'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'category']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
