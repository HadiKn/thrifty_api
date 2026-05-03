from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255 , unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name
    
    def get_all_descendants(self):
        """Get all descendant categories recursively"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_all_ancestors(self):
        """Get all ancestor categories recursively"""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors
    
    def get_family_tree(self):
        """Get entire family tree (ancestors + self + descendants)"""
        return {
            'ancestors': self.get_all_ancestors(),
            'self': self,
            'descendants': self.get_all_descendants()
        }