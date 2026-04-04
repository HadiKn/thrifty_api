from django.db import models
from users.models import User


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(balance__gte=0), name='wallet_balance_non_negative'),
        ]

    def __str__(self):
        return f'{self.user_id} — {self.balance}'


class WalletTransaction(models.Model):
    """
    Ledger row: every balance change should create one of these.
    amount: positive = credit (money in), negative = debit (money out).
    """

    class Kind(models.TextChoices):
        ADMIN_TOPUP = 'admin_topup', 'Admin top-up'
        PURCHASE = 'purchase', 'Purchase'
        REFUND = 'refund', 'Refund'
        AUCTION_PAYMENT = 'auction_payment', 'Auction payment'
        ADJUSTMENT = 'adjustment', 'Manual adjustment'

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    reference_type = models.CharField(max_length=32, blank=True)
    reference_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.kind} {self.amount} → balance {self.balance_after}'
