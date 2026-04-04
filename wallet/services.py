from decimal import Decimal
from django.db import transaction
from .models import Wallet, WalletTransaction


class WalletService:
    
    @staticmethod
    def get_or_create_wallet(user):
        """Get existing wallet or create new one for user"""
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet
    
    @staticmethod
    @transaction.atomic
    def process_topup(wallet, amount, description="Wallet top-up"):
        """Add funds to wallet"""
        if amount <= 0:
            raise ValueError("Top-up amount must be positive")
        
        # Calculate new balance
        new_balance = wallet.balance + amount
        
        # Create transaction record
        transaction_record = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            balance_after=new_balance,
            kind=WalletTransaction.Kind.ADMIN_TOPUP,
            description=description
        )
        
        # Update wallet balance
        wallet.balance = new_balance
        wallet.save()
        
        return transaction_record
    
    
    
    @staticmethod
    @transaction.atomic
    def process_refund(wallet, amount, reference_type="", reference_id="", description="Refund"):
        """Refund funds to wallet"""
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        # Calculate new balance
        new_balance = wallet.balance + amount
        
        # Create transaction record
        transaction_record = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            balance_after=new_balance,
            kind=WalletTransaction.Kind.REFUND,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        
        # Update wallet balance
        wallet.balance = new_balance
        wallet.save()
        
        return transaction_record
    
    @staticmethod
    @transaction.atomic
    def process_complete_purchase(buyer_wallet, seller_wallet, amount, reference_type="", reference_id="", description="Purchase"):
        if amount <= 0:
            raise ValueError("Purchase amount must be positive")
        
        if buyer_wallet.balance < amount:
            raise ValueError("Insufficient buyer wallet balance")
        
        buyer_new_balance = buyer_wallet.balance - amount
        buyer_transaction = WalletTransaction.objects.create(
            wallet=buyer_wallet,
            amount=-amount,
            balance_after=buyer_new_balance,
            kind=WalletTransaction.Kind.PURCHASE,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"{description} - Payment"
        )
        buyer_wallet.balance = buyer_new_balance
        buyer_wallet.save()
        
        seller_new_balance = seller_wallet.balance + amount
        seller_transaction = WalletTransaction.objects.create(
            wallet=seller_wallet,
            amount=amount, 
            balance_after=seller_new_balance,
            kind=WalletTransaction.Kind.PURCHASE,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"{description} - Sale"
        )
        seller_wallet.balance = seller_new_balance
        seller_wallet.save()
        
        return {
            'buyer_transaction': buyer_transaction,
            'seller_transaction': seller_transaction,
            'amount': amount
        }
    
    @staticmethod
    @transaction.atomic
    def process_auction_payment(wallet, amount, reference_type="", reference_id="", description="Auction payment"):
        """Process payment for won auction"""
        if amount <= 0:
            raise ValueError("Auction payment amount must be positive")
        
        if wallet.balance < amount:
            raise ValueError("Insufficient wallet balance for auction payment")
        
        # Calculate new balance
        new_balance = wallet.balance - amount
        
        # Create transaction record
        transaction_record = WalletTransaction.objects.create(
            wallet=wallet,
            amount=-amount,  # Negative for debit
            balance_after=new_balance,
            kind=WalletTransaction.Kind.AUCTION_PAYMENT,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        
        # Update wallet balance
        wallet.balance = new_balance
        wallet.save()
        
        return transaction_record
