from django.db import models
from users.models import User
from items.models import Item

class Report(models.Model):
    class ReportStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'
    
    class ReportReason(models.TextChoices):
        INAPPROPRIATE_CONTENT = 'inappropriate_content', 'Inappropriate Content'
        FRAUD = 'fraud', 'Fraud'
        SPAM = 'spam', 'Spam'
        HARASSMENT = 'harassment', 'Harassment'
        SCAM = 'scam', 'Scam'
        OTHER = 'other', 'Other'    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reports')    
    reason = models.CharField(max_length=30, choices=ReportReason.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    admin_notes = models.TextField(blank=True, help_text="Admin resolution notes")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report on item: {self.reported_item.name} by {self.reporter.username}"