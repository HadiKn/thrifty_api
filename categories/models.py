from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255 , unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name