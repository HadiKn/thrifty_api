from celery import shared_task
from django.utils import timezone
from .models import Auction, Bid, Claim
from wallet.services import WalletService
from chat.services import send_auction_winner_notification
import logging

logger = logging.getLogger(__name__)


@shared_task
def end_expired_auctions():
    """End auctions that have passed their end time"""
    now = timezone.now()
    expired_auctions = list(Auction.objects.filter(
        status=Auction.AuctionStatus.ACTIVE,
        end_time__lte=now
    ))

    for auction in expired_auctions:
        try:
            process_auction_winner(auction)
        except Exception:
            logger.exception("Failed to process auction %s", auction.id)

    return {
        "message": f"Processed {len(expired_auctions)} expired auctions",
        "count": len(expired_auctions)
    }


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
                reference_id=str(auction.item.id),
                buyer_description=f"Payment for auction: {auction.item.name}",
                seller_description=f"Auction sale: {auction.item.name}"
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

            try:
                send_auction_winner_notification(auction, highest_bid.bidder)
            except Exception:
                logger.exception(
                    "Failed to notify winner of auction %s", auction.id
                )

        except ValueError as e:
            # Insufficient funds - mark auction as ended but no winner
            auction.status = Auction.AuctionStatus.ENDED
            auction.save()
            logger.warning("Payment failed for auction %s: %s", auction.id, e)
    else:
        # No bids - just end auction
        auction.status = Auction.AuctionStatus.CANCELLED
        auction.save()

    # The auction is over either way - the item is no longer listed
    auction.item.is_available = False
    auction.item.save(update_fields=["is_available"])