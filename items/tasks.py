from celery import shared_task
from django.utils import timezone
from .models import Auction, Bid, Claim
from wallet.services import WalletService

@shared_task
def end_expired_auctions():
    """End auctions that have passed their end time"""
    now = timezone.now()
    expired_auctions = Auction.objects.filter(
        status=Auction.AuctionStatus.ACTIVE,
        end_time__lte=now
    )
    
    for auction in expired_auctions:
        process_auction_winner(auction)
    
    return f"Processed {expired_auctions.count()} expired auctions"

def process_auction_winner(auction):
    """Process the auction winner and handle payment"""
    # Get highest bid
    highest_bid = auction.bids.order_by('-bid_amount').first()
    
    if highest_bid:
        # Check winner's balance at auction end
        buyer_wallet = WalletService.get_or_create_wallet(highest_bid.bidder)
        seller_wallet = WalletService.get_or_create_wallet(auction.item.owner)
        
        try:
            # Only process payment if winner has sufficient funds
            WalletService.process_complete_purchase(
                buyer_wallet=buyer_wallet,
                seller_wallet=seller_wallet,
                amount=highest_bid.bid_amount,
                reference_type="auction",
                reference_id=auction.id,
                description=f"Auction winner: {auction.item.name}"
            )
            
            # Create claim
            Claim.objects.create(
                item=auction.item,
                buyer=highest_bid.bidder
            )
            
            # Update statuses
            auction.status = Auction.AuctionStatus.ENDED
            auction.winner = highest_bid.bidder
            auction.save()
            
            auction.item.is_available = False
            auction.item.save()
            
        except ValueError as e:
            # Insufficient funds - mark auction as ended but no winner
            auction.status = Auction.AuctionStatus.ENDED
            auction.save()
            print(f"Payment failed for auction {auction.id}: {e}")
    else:
        # No bids - just end auction
        auction.status = Auction.AuctionStatus.ENDED
        auction.save()